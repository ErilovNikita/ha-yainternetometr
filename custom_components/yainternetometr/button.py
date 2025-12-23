from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_NAME, DEVICE_IDENTIFIER

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