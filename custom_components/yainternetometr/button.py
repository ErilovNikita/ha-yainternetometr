from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_NAME, DEVICE_IDENTIFIER

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        YaInternetometrUpdateButton(hass, entry, coordinator)
    ])

class YaInternetometrUpdateButton(ButtonEntity):
    """Button to trigger an immediate speed test update."""

    def __init__(self, coordinator: DataUpdateCoordinator):
        # Metrics
        self.coordinator = coordinator
        self._attr_name = "Update SpeedTest"
        self._attr_unique_id = "ya_speedtest_update"
        self._attr_icon = "mdi:refresh"

        # General information about "Device" for combining all sensors
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DEVICE_IDENTIFIER)},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()