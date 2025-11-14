# custom_components/yainternetometr/__init__.py

from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL, SENSOR_PING, SENSOR_DOWNLOAD, SENSOR_UPLOAD
from yaspeedtest.client import YaSpeedTest

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = YaInternetometrDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class YaInternetometrDataUpdateCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="YaInternetometr Data Coordinator",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, float]:
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
        except Exception as err:
            raise UpdateFailed(f"Error fetch data: {err}") from err