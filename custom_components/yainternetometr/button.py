
from __future__ import annotations
import logging
from collections.abc import Callable, Awaitable

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
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
        - async_add_entities (AddEntitiesCallback): A callback function used to create and add entities (buttons) to Home Assistant.

    Returns:
        None
    """

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async def refresh_data():
        await coordinator.async_request_refresh()

    buttons = [
        YaInternetometrButton(coordinator, entry, "update_speedtest", "update_now", "mdi:refresh", refresh_data)
    ]

    async_add_entities(buttons)
    _LOGGER.debug("Created %d buttons YaInternetometr", len(buttons))

class YaInternetometrButton(CoordinatorEntity, ButtonEntity):
    """
    YaInternetometr integration button it in Home Assistant.

    The class inherits:
        - ButtonEntity: Standard button interface in Home Assistant.

    Attributes:
        `coordinator`: A YaInternetometrDataUpdateCoordinator instance, providing up-to-date ping, download, and upload values.
        `_attr_translation_key` (str): The key for the display name in the Home Assistant interface.
        `_attr_icon` (str): button icon for the UI (Material Design Icons).
        `_attr_unique_id` (str): unique button identifier within the integration.
        `_attr_device_info` (dict): information about the device to which the buttons are linked. Combines all buttons into a single logical device, "YaInternetometr".

    Methods:
        `__init__`: initializes the button, assigns attributes, and links it to the data update coordinator.
    """

    def __init__(
            self, 
            coordinator: DataUpdateCoordinator,
            entry: ConfigEntry,
            unique_id: str, 
            translation_key: str, 
            icon: str,
            press_action: Callable[[], Awaitable[None]],
    ):
        """Initializing the YaInternetometr button."""

        # Metrics
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry.entry_id}_{unique_id}"
        self._default_icon = icon
        self._press_action = press_action
        self._in_progress = False

        # General information about "Device" for combining all buttons
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DEVICE_IDENTIFIER)},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
        }

    async def async_press(self):
        if self._in_progress or self.coordinator._update_lock.locked():
            _LOGGER.debug("Speedtest already in progress — skipping refresh")
            return

        self._in_progress = True
        self.async_write_ha_state()

        try:
            await self._press_action()
        finally:
            self._in_progress = False
            self.async_write_ha_state()

    @property
    def available(self):
        return not self._in_progress
    
    @property
    def extra_state_attributes(self):
        return {"in_progress": self._in_progress}
    
    @property
    def icon(self):
        return "mdi:progress-clock" if self._in_progress else self._default_icon