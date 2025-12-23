from datetime import timedelta
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL, MAX_SCAN_INTERVAL, MIN_SCAN_INTERVAL, STEP_SCAN_INTERVAL

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        UpdateIntervalNumber(hass, entry, coordinator)
    ])

class UpdateIntervalNumber(NumberEntity):
    _attr_name = "Update interval"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_native_min_value = MIN_SCAN_INTERVAL
    _attr_native_max_value = MAX_SCAN_INTERVAL
    _attr_native_step = STEP_SCAN_INTERVAL

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator):
        self.hass = hass
        self.entry = entry
        self.coordinator = coordinator

        self._attr_unique_id = f"{entry.entry_id}_update_interval"

        self._attr_native_value = entry.options.get(
            CONF_UPDATE_INTERVAL,
            DEFAULT_SCAN_INTERVAL
        )

    async def async_set_native_value(self, value: float) -> None:
        value = int(value)

        self._attr_native_value = value

        self.hass.config_entries.async_update_entry(
            self.entry,
            options={**self.entry.options, CONF_UPDATE_INTERVAL: value},
        )

        self.coordinator.update_interval = timedelta(seconds=value)