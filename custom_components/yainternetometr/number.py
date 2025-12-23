from datetime import timedelta
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL, MAX_SCAN_INTERVAL, MIN_SCAN_INTERVAL, STEP_SCAN_INTERVAL, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_NAME, DEVICE_IDENTIFIER

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        YaInternetometrNumber(hass, entry, coordinator)
    ])

class YaInternetometrNumber(NumberEntity):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator):
        """Initializing the YaInternetometr number."""

        # Metrics
        self._attr_name = "Update interval"
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        self._attr_native_min_value = MIN_SCAN_INTERVAL
        self._attr_native_max_value = MAX_SCAN_INTERVAL
        self._attr_native_step = STEP_SCAN_INTERVAL
        self.hass = hass
        self.entry = entry
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_update_interval"

        self._attr_native_value = entry.options.get(
            CONF_UPDATE_INTERVAL,
            DEFAULT_SCAN_INTERVAL
        )

        # General information about "Device" for combining all sensors
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DEVICE_IDENTIFIER)},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
        }

    async def async_set_native_value(self, value: float) -> None:
        minutes = int(value)

        self._attr_native_value = minutes
        self.coordinator.update_interval = timedelta(minutes=minutes)

        self.hass.config_entries.async_update_entry(
            self.entry,
            options={
                **self.entry.options, 
                CONF_UPDATE_INTERVAL: minutes
            },
        )

        await self.coordinator.async_request_refresh()