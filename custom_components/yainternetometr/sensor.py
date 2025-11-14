# custom_components/yainternetometr/sensors.py

from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_PING, SENSOR_DOWNLOAD, SENSOR_UPLOAD

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensors = [
        YaInternetometrSensor(coordinator, SENSOR_PING, "Ping", "ms", "mdi:timer"),
        YaInternetometrSensor(coordinator, SENSOR_DOWNLOAD, "Download", "Mbps", "mdi:download"),
        YaInternetometrSensor(coordinator, SENSOR_UPLOAD, "Upload", "Mbps", "mdi:upload"),
    ]

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.debug("Created %d sensors YaInternetometr", len(sensors))


class YaInternetometrSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, sensor_type: str, name: str, unit: str, icon: str):
        super().__init__(coordinator)

        self.sensor_type = sensor_type
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, "internet_test")},
            "name": "YaInternetometr",
            "manufacturer": "Yandex",
            "model": "Internetometr",
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self.sensor_type) if self.coordinator.data else None