# custom_components/yainternetometr/__init__.py

from __future__ import annotations
import asyncio
from asyncio import timeout
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL, SENSOR_PING, SENSOR_DOWNLOAD, SENSOR_UPLOAD, TIMEOUT_TEST
from yaspeedtest.client import YaSpeedTest

_LOGGER = logging.getLogger(__name__)

UPLOAD_CLASSIC_FALLBACK_SIZE = 1_000_000


def _normalize_rate_mbps(value: float | int | None, metric_name: str) -> float:
    """Normalize speed value to Mbit/s.

    `yaspeedtest` should return Mbps, but some providers/versions may return bps.
    This helper keeps current behavior for normal values and rescales only obviously
    out-of-range numbers.
    """

    if value is None:
        return 0.0

    rate = float(value)
    if rate < 0:
        _LOGGER.warning("Received negative %s value: %s", metric_name, value)
        return 0.0

    # Defensive conversion: values in hundreds of thousands are likely bps.
    if rate > 100_000:
        converted = rate / 1_000_000
        _LOGGER.debug(
            "Converted %s from bps to Mbit/s: raw=%s normalized=%.3f",
            metric_name,
            value,
            converted,
        )
        return converted

    return rate


def _result_mapping(result: object) -> dict | None:
    """Return a dict-like view for provider results that expose one."""
    if isinstance(result, dict):
        return result

    for method_name in ("model_dump", "as_dict", "dict"):
        method = getattr(result, method_name, None)
        if callable(method):
            try:
                data = method()
            except Exception:
                continue
            if isinstance(data, dict):
                return data

    return None


def _extract_rate_mbps(result: object, *candidates: str) -> float | int | None:
    """Extract speed value from provider result using multiple documented/legacy names."""
    mapping = _result_mapping(result)

    for field_name in candidates:
        if hasattr(result, field_name):
            return getattr(result, field_name)
        if mapping is not None and field_name in mapping:
            return mapping[field_name]
    return None


def _extract_ping_ms(result: object) -> float:
    """Extract ping from a provider result."""
    return float(_extract_rate_mbps(result, "ping_ms", "ping") or 0)


def _extract_download_mbps(result: object, metric_name: str = "download") -> float:
    """Extract and normalize download speed from a provider result."""
    return _normalize_rate_mbps(
        _extract_rate_mbps(
            result,
            "download_mbps",
            "download_mbit",
            "download_mbit_s",
            "download",
            "download_bps",
        ),
        metric_name,
    )


def _extract_upload_mbps(result: object, metric_name: str = "upload") -> float:
    """Extract and normalize upload speed from a provider result."""
    return _normalize_rate_mbps(
        _extract_rate_mbps(
            result,
            "upload_mbps",
            "upload_mbit",
            "upload_mbit_s",
            "upload",
            "upload_bps",
        ),
        metric_name,
    )


def _get_value(source: object, field_name: str, default: object = None) -> object:
    """Read a field from an object or dict."""
    if isinstance(source, dict):
        return source.get(field_name, default)
    return getattr(source, field_name, default)


async def _measure_upload_fallback_mbps(ya: YaSpeedTest) -> float:
    """Measure upload directly from available upload probes."""
    upload = _get_value(_get_value(ya, "probes"), "upload")
    probes = _get_value(upload, "probes", []) or []
    best_upload_mbps = 0.0

    for probe_idx, probe in enumerate(probes, start=1):
        url = _get_value(probe, "url")
        size = _get_value(probe, "size")
        probe_timeout = _get_value(probe, "timeout")

        try:
            size_int = int(size or 0)
        except (TypeError, ValueError):
            size_int = 0

        if not url or size_int <= 0:
            _LOGGER.debug(
                "Skipping upload fallback probe #%d: url=%s size=%s",
                probe_idx,
                url,
                size,
            )
            continue

        try:
            raw_upload_mbps = await ya.measure_upload_peak(url, size_int, probe_timeout)
        except asyncio.CancelledError:
            raise
        except Exception as err:
            _LOGGER.debug(
                "Upload fallback probe #%d failed: %s",
                probe_idx,
                err,
            )
            continue

        upload_mbps = _normalize_rate_mbps(
            raw_upload_mbps,
            f"upload_fallback_probe_{probe_idx}",
        )

        if upload_mbps == 0 and hasattr(ya, "measure_upload"):
            classic_size = max(size_int, UPLOAD_CLASSIC_FALLBACK_SIZE)
            _LOGGER.debug(
                "Running classic upload fallback probe #%d: probe_size=%d classic_size=%d",
                probe_idx,
                size_int,
                classic_size,
            )
            try:
                elapsed, uploaded_bytes = await ya.measure_upload(
                    url,
                    classic_size,
                    probe_timeout,
                )
            except asyncio.CancelledError:
                raise
            except Exception as err:
                _LOGGER.debug(
                    "Classic upload fallback probe #%d failed: %s",
                    probe_idx,
                    err,
                )
            else:
                if elapsed and elapsed != float("inf") and uploaded_bytes > 0:
                    classic_upload_mbps = (uploaded_bytes * 8) / elapsed / 1_000_000
                    upload_mbps = _normalize_rate_mbps(
                        classic_upload_mbps,
                        f"upload_classic_fallback_probe_{probe_idx}",
                    )
                    _LOGGER.debug(
                        "Classic upload fallback probe #%d result: %.2f Mbit/s",
                        probe_idx,
                        upload_mbps,
                    )

        _LOGGER.debug(
            "Upload fallback probe #%d result: %.2f Mbit/s",
            probe_idx,
            upload_mbps,
        )
        best_upload_mbps = max(best_upload_mbps, upload_mbps)

    if best_upload_mbps > 0:
        _LOGGER.info(
            "Using direct upload fallback result: %.2f Mbit/s",
            best_upload_mbps,
        )

    return best_upload_mbps


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Configuring the YaInternetometr integration via a configuration entry (UI).

    This method is called by Home Assistant when the user adds an integration via the interface (config flow). It is responsible for creating and registering
    the data update coordinator and subsequently loading the platforms (sensors).

    Parameters:
        `hass` (HomeAssistant): The main Home Assistant object, providing access to the platform's data, services, and components.
        `entry` (ConfigEntry): The configuration entry for the current integration, contains the unique identifier entry_id and the saved configuration data.

    Method actions:
        1. Creates a YaInternetometrDataUpdateCoordinator instance, which will periodically poll the YaSpeedTest service.
        2. Calls async_config_entry_first_refresh() to obtain initial data before displaying sensors.
        3. Registers the coordinator in hass.data under the unique identifier of the configuration entry entry.entry_id.
        4. Loads the sensor platform via async_forward_entry_setups so that Home Assistant can create the corresponding SensorEntity.
        5. Returns True if setup was successful.

    Return value:
        bool: True if integration setup was successful, False if an error occurred.
    """

    scan_interval:any = entry.options.get(
        CONF_UPDATE_INTERVAL,
        DEFAULT_SCAN_INTERVAL,
    )

    update_interval = (
        timedelta(minutes=scan_interval)
        if scan_interval > 0 else None
    )

    coordinator = YaInternetometrDataUpdateCoordinator(hass, entry, update_interval)

    if update_interval is not None:
        hass.async_create_task(
            coordinator.async_config_entry_first_refresh()
        )
    else:
        _LOGGER.info(
            "YaInternetometr started with update interval = 0, "
            "automatic updates disabled"
        )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number", "button"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unloading the YaInternetometr integration when deleting or disabling a configuration entry.

    This method is called by Home Assistant when the user deletes an integration through the interface or disables a configuration entry. It is responsible for the correct
    deletion of platforms (sensors) and clearing of integration data.

    Parameters:
        `hass` (HomeAssistant): The main Home Assistant object, providing access to platform data, services, and components.
        `entry` (ConfigEntry): The configuration entry for the current integration, contains the unique identifier entry_id and the saved configuration data.

    Method actions:
        1. Calls async_unload_platforms to unload all platforms associated
        with this configuration entry (in our case, sensors).
        2. If the unload is successful, deletes the coordinator and associated data
        from hass.data by the entry.entry_id key.
        3. Returns the result of unloading the platforms.

    Return value:
        `bool`: True if the platforms were successfully unloaded and the data cleared. False if the upload failed.
    """

    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "number", "button"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class YaInternetometrDataUpdateCoordinator(DataUpdateCoordinator):
    """
    A coordinator for periodic YaInternetometr data updates.

    This class inherits Home Assistant's DataUpdateCoordinator, providing convenient management of asynchronous data updates, caching, and notification of sensors when state changes.

    Main Purpose:
        - Periodically run a speed test via YaSpeedTest.
        - Store results (ping, download, upload) in coordinator.data.
        - Ensure automatic updates of all associated sensors.

    Attributes:
        `hass` (HomeAssistant): The main Home Assistant object.
        `_LOGGER` (Logger): Logger for outputting debug information.
        `name` (str): The name of the coordinator, used in logs.
        `update_interval` (timedelta): The automatic data update interval.

    Methods:
        `__init__`: Initializes the coordinator.
        `_async_update_data`: An asynchronous method that Home Assistant calls to obtain new data with each update.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, update_interval: timedelta | None) -> None:
        """
        Coordinator initialization.

        Parameters:
            `hass` (HomeAssistant): The main Home Assistant object through which interaction with the platform occurs.
        """

        super().__init__(
            hass,
            _LOGGER,
            name="YaInternetometr Data Coordinator",
            update_interval=update_interval
        )
        self._update_lock = asyncio.Lock()

    async def _async_update_data(self) -> dict[str, float]:
        """
        Asynchronous data update from the YaSpeedTest service.

        This method is called automatically by Home Assistant for each update.
        It creates a YaSpeedTest client, runs a speed test, and returns a dictionary
        with the results:
        
        ```
        {
            "ping": <float>, # latency in milliseconds
            "download": <float>, # download speed in Mbps
            "upload": <float>, # upload speed in Mbps
        }
        ```
        """

        if self._update_lock.locked() and self.data is not None:
            _LOGGER.debug("Speedtest already running — skipping update")
            return self.data
    
        async with self._update_lock:
            try:
                async with timeout(TIMEOUT_TEST):
                    ya = await YaSpeedTest.create()
                    result = await ya.run()
                    _LOGGER.debug("Raw YaSpeedTest result payload: %s", result)

                    upload_mbps = _extract_upload_mbps(result)
                    download_mbps = _extract_download_mbps(result)
                    ping_ms = _extract_ping_ms(result)

                    if upload_mbps == 0 and download_mbps > 1:
                        _LOGGER.warning(
                            "Upload speed is zero while download is %.2f Mbit/s. "
                            "Trying direct upload probe fallback first.",
                            download_mbps,
                        )

                        fallback_upload_mbps = await _measure_upload_fallback_mbps(ya)
                        if fallback_upload_mbps > upload_mbps:
                            upload_mbps = fallback_upload_mbps

                        if upload_mbps == 0:
                            _LOGGER.warning(
                                "Direct upload probe fallback returned 0.00 Mbit/s. "
                                "Running up to 2 extra verification passes.",
                            )

                            for retry_idx in range(2):
                                # Small cooldown gives providers a chance to finish
                                # server-side aggregation for upload values.
                                await asyncio.sleep(1.5)

                                retry = await YaSpeedTest.create()
                                retry_result = await retry.run()
                                _LOGGER.debug(
                                    "Retry #%d YaSpeedTest result payload: %s",
                                    retry_idx + 1,
                                    retry_result,
                                )

                                retry_upload = _extract_upload_mbps(
                                    retry_result,
                                    f"upload_retry_{retry_idx + 1}",
                                )
                                retry_download = _extract_download_mbps(
                                    retry_result,
                                    f"download_retry_{retry_idx + 1}",
                                )

                                if retry_upload > upload_mbps:
                                    _LOGGER.info(
                                        "Using retry upload result: current=%.2f Mbit/s retry=%.2f Mbit/s",
                                        upload_mbps,
                                        retry_upload,
                                    )
                                    upload_mbps = retry_upload

                                if retry_download > download_mbps:
                                    download_mbps = retry_download

                                if upload_mbps > 0:
                                    break

                        if upload_mbps == 0:
                            previous_upload = (
                                float(self.data.get(SENSOR_UPLOAD, 0.0))
                                if self.data is not None
                                else 0.0
                            )
                            if previous_upload > 0:
                                _LOGGER.warning(
                                    "Fresh upload measurement remains 0.00 Mbit/s; "
                                    "keeping previous non-zero value %.2f Mbit/s",
                                    previous_upload,
                                )
                                upload_mbps = previous_upload
                            else:
                                _LOGGER.warning(
                                    "Fresh upload measurement remains 0.00 Mbit/s "
                                    "and no previous non-zero value is available.",
                                )

                    _LOGGER.debug(
                        "SpeedTest results: ping=%.2f ms, download=%.2f Mbps, upload=%.2f Mbps",
                        ping_ms,
                        download_mbps,
                        upload_mbps,
                    )
                    data = {
                        SENSOR_PING: ping_ms,
                        SENSOR_DOWNLOAD: download_mbps,
                        SENSOR_UPLOAD: upload_mbps,
                    }
                    self.async_set_updated_data(data)
                    return data
                
            except TimeoutError as err:
                raise UpdateFailed("Speedtest timed out") from err

            except asyncio.CancelledError:
                _LOGGER.debug("Yandex Speedtest measurement was cancelled — skipping update")
                raise

            except Exception as err:
                _LOGGER.error("Error during Yandex Speedtest update: %s", err)
                raise UpdateFailed(f"Error fetching data: {err}") from err
