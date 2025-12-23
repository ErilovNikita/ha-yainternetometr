
from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_NAME, DEVICE_IDENTIFIER

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant, 
        entry: ConfigEntry, 
        async_add_entities: AddEntitiesCallback
) -> None:
    """
    Initializing YaInternetometr integration buttons when added via the UI.

    This method is called by Home Assistant after the user has added an integration
    through the configuration interface (config flow). It is responsible for creating button objects
    and registering them in the system.

    Parameters:
        - hass (HomeAssistant): The main Home Assistant object, providing access to data, services, and other platform components.
        - entry (ConfigEntry): The configuration entry for the current integration. Contains a
        - unique identifier, configuration data, and integration state.
        - async_add_entities (AddEntitiesCallback): A callback function used to create and add entities (sensors) to Home Assistant.

    Returns:
        None
    """

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async def refresh_data():
        await coordinator.async_request_refresh()

    buttons = [
        YaInternetometrButton(hass, entry, coordinator, "update_speedtest", "Update speedtest", "mdi:refresh", refresh_data)
    ]

    async_add_entities(buttons, update_before_add=True)
    _LOGGER.debug("Created %d buttons YaInternetometr", len(buttons))

class YaInternetometrButton(ButtonEntity):
    """
    YaInternetometr integration button it in Home Assistant.

    The class inherits:
        - ButtonEntity: Standard button interface in Home Assistant.

    Attributes:
        `coordinator`: A YaInternetometrDataUpdateCoordinator instance, providing up-to-date ping, download, and upload values.
        `_attr_name` (str): The button's display name in the HA interface.
        `_attr_icon` (str): button icon for the UI (Material Design Icons).
        `_attr_unique_id` (str): unique button identifier within the integration.
        `_attr_device_info` (dict): information about the device to which the sensors are linked. Combines all sensors into a single logical device, "YaInternetometr".

    Methods:
        `__init__`: initializes the sensor, assigns attributes, and links it to the data update coordinator.
    """

    def __init__(
            self, 
            coordinator: DataUpdateCoordinator,
            unique_id: str, 
            name: str, 
            icon: str,
            press_action: callable,
    ):
        """Initializing the YaInternetometr button."""

        # Metrics
        self.coordinator = coordinator
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_button_{unique_id}"
        self._attr_icon = icon
        self._press_action = press_action

        # General information about "Device" for combining all sensors
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DEVICE_IDENTIFIER)},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        if callable(self._press_action):
            await self._press_action()