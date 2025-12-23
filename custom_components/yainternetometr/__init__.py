# custom_components/yainternetometr/__init__.py

from __future__ import annotations
import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL, SENSOR_PING, SENSOR_DOWNLOAD, SENSOR_UPLOAD
from yaspeedtest.client import YaSpeedTest

_LOGGER = logging.getLogger(__name__)


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

    coordinator = YaInternetometrDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

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

    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
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

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """
        Coordinator initialization.

        Parameters:
            `hass` (HomeAssistant): The main Home Assistant object through which interaction with the platform occurs.
        """

        scan_interval:any = entry.options.get(
            CONF_UPDATE_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )

        if isinstance(scan_interval, timedelta):
            update_interval:timedelta = scan_interval
        else:
            update_interval:timedelta = timedelta(minutes=scan_interval)

        super().__init__(
            hass,
            _LOGGER,
            name="YaInternetometr Data Coordinator",
            update_interval=update_interval
        )

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
        try:
            ya = await YaSpeedTest().create()
            result = await ya.run()
            _LOGGER.debug(
                "SpeedTest results: ping=%.2f ms, download=%.2f Mbps, upload=%.2f Mbps",
                result.ping_ms, result.download_mbps, result.upload_mbps
            )
            return {
                SENSOR_PING: result.ping_ms,
                SENSOR_DOWNLOAD: result.download_mbps,
                SENSOR_UPLOAD: result.upload_mbps,
            }

        except asyncio.CancelledError:
            _LOGGER.warning("Yandex Speedtest measurement was cancelled — skipping update")
            return None

        except Exception as err:
            _LOGGER.error("Error during Yandex Speedtest update: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err