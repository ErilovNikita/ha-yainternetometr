from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTime
from datetime import timedelta

from .const import DOMAIN, CONF_UPDATE_INTERVAL, MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL, STEP_SCAN_INTERVAL

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([UpdateIntervalNumber(coordinator)])


class UpdateIntervalNumber(NumberEntity):
    _attr_name = "Update interval"
    _attr_unique_id = f"{DOMAIN}_{CONF_UPDATE_INTERVAL}"
    _attr_unit_of_measurement = UnitOfTime.SECONDS
    _attr_min_value = MIN_SCAN_INTERVAL
    _attr_max_value = MAX_SCAN_INTERVAL
    _attr_step = STEP_SCAN_INTERVAL
    _attr_mode = "box"
    _attr_icon = "mdi:timer-cog"

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_native_value = int(
            coordinator.update_interval.total_seconds()
        )

    async def async_set_native_value(self, value: float) -> None:
        seconds = int(value)
        self._attr_native_value = seconds

        self.coordinator.update_interval = timedelta(seconds=seconds)

        await self.coordinator.async_request_refresh()