from __future__ import annotations
import logging

from datetime import timedelta
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL, MAX_SCAN_INTERVAL, MIN_SCAN_INTERVAL, STEP_SCAN_INTERVAL, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_NAME, DEVICE_IDENTIFIER

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant, 
        entry: ConfigEntry, 
        async_add_entities: AddEntitiesCallback
) -> None:
    """
    Initializing YaInternetometr integration number when added via the UI.

    This method is called by Home Assistant after the user has added an integration
    through the configuration interface (config flow). It is responsible for creating number objects
    and registering them in the system.

    Parameters:
        - hass (HomeAssistant): The main Home Assistant object, providing access to data, services, and other platform components.
        - entry (ConfigEntry): The configuration entry for the current integration. Contains a
        - unique identifier, configuration data, and integration state.
        - async_add_entities (AddEntitiesCallback): A callback function used to create and add entities (numbers) to Home Assistant.

    Returns:
        None
    """
        
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    numbers = [
        YaInternetometrNumber(hass, entry, coordinator)
    ]
    
    async_add_entities(numbers, update_before_add=True)
    _LOGGER.debug("Created %d numbers YaInternetometr", len(numbers))

class YaInternetometrNumber(NumberEntity, RestoreEntity):
    """
    YaInternetometr integration number it in Home Assistant.

    The class inherits:
        - NumberEntity: Standard number interface in Home Assistant.
        - RestoreEntity: Standard restore interface in Home Assistant.

    Attributes:
        `coordinator`: A YaInternetometrDataUpdateCoordinator instance, providing up-to-date ping, download, and upload values.
        `_attr_name` (str): The number's display name in the HA interface.
        `_attr_icon` (str): number icon for the UI (Material Design Icons).
        `_attr_unique_id` (str): unique number identifier within the integration.
        `_attr_device_info` (dict): information about the device to which the numbers are linked. Combines all numbers into a single logical device, "YaInternetometr".

    Methods:
        `__init__`: initializes the number, assigns attributes, and links it to the data update coordinator.
    """
        
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator: DataUpdateCoordinator):
        """Initializing the YaInternetometr number."""

        # Metrics
        self._attr_name = "Update interval"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
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

        # General information about "Device" for combining all numbers
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DEVICE_IDENTIFIER)},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
        }

    async def async_set_native_value(self, value: float) -> None:
        minutes = int(value)

        self._attr_native_value = minutes

        if minutes == 0:
            self.coordinator.update_interval = None
        else:
            self.coordinator.update_interval = timedelta(minutes=minutes)

        self.hass.config_entries.async_update_entry(
            self.entry,
            options={
                **self.entry.options, 
                CONF_UPDATE_INTERVAL: minutes
            },
        )

        await self.coordinator.async_request_refresh()
    
    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        if (state := await self.async_get_last_state()):
            try:
                value = int(state.state)
            except ValueError:
                return

            self._attr_native_value = value
            self.coordinator.update_interval = timedelta(minutes=value)