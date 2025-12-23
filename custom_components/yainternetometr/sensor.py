# custom_components/yainternetometr/sensors.py

from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_PING, SENSOR_DOWNLOAD, SENSOR_UPLOAD, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_NAME, DEVICE_IDENTIFIER

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Initializing YaInternetometr integration sensors when added via the UI.

    This method is called by Home Assistant after the user has added an integration
    through the configuration interface (config flow). It is responsible for creating sensor objects
    and registering them in the system.

    Parameters:
    hass (HomeAssistant): The main Home Assistant object, providing access
    to data, services, and other platform components.
    entry (ConfigEntry): The configuration entry for the current integration. Contains a
    unique identifier, configuration data, and integration state.
    async_add_entities (AddEntitiesCallback): A callback function used to create and add entities (sensors) to Home Assistant.

    Method actions:
    1. Gets the data update coordinator from hass.data for the current entry.
    2. Creates three sensors:
    - Ping: Network response time in milliseconds.
    - Download: Download speed in Mbps.
    - Upload: upload speed in Mbit/s.
    3. Each sensor is assigned:
    - name,
    - data type for state_class and device_class,
    - units of measurement,
    - icon for display in the interface.
    4. Registers sensors via `async_add_entities`, ensuring that values ​​are updated before the first display (`update_before_add=True`).
    5. Logs the number of created sensors for debugging.

    Returns:
    None
    """

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensors = [
        YaInternetometrSensor(coordinator, SENSOR_PING, "Ping", None, "ms", "mdi:cloud-refresh-variant"),
        YaInternetometrSensor(coordinator, SENSOR_DOWNLOAD, "Download", "data_rate", "Mbit/s", "mdi:cloud-download"),
        YaInternetometrSensor(coordinator, SENSOR_UPLOAD, "Upload", "data_rate", "Mbit/s", "mdi:cloud-upload"),
    ]

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.debug("Created %d sensors YaInternetometr", len(sensors))


class YaInternetometrSensor(CoordinatorEntity, SensorEntity):
    """
    YaInternetometr integration sensor that receives data from
    DataUpdateCoordinator and displays it in Home Assistant.

    The class inherits:
        - CoordinatorEntity: Provides automatic updating
        of sensor values ​​when coordinator data changes.
        - SensorEntity: Standard sensor interface in Home Assistant.

    Attributes:
        `coordinator`: A YaInternetometrDataUpdateCoordinator instance, providing up-to-date ping, download, and upload values.
        `sensor_type` (str): The metric type corresponding to the key in `coordinator.data`. For example, "ping", "download", "upload".
        `_attr_name` (str): The sensor's display name in the HA interface.
        `_attr_state_class` (str): Specifies that the sensor measures a continuous value ("measurement"), to support history and graphs.
        `_attr_native_unit_of_measurement` (str): Units of measurement, for example, "ms" or "Mbit/s".
        `_attr_icon` (str): sensor icon for the UI (Material Design Icons).
        `_attr_unique_id` (str): unique sensor identifier within the integration.
        `_attr_device_class` (str | None): standard Home Assistant device class for correctly displaying the data type (e.g., "data_rate").
        `_attr_device_info` (dict): information about the device to which the sensors are linked. Combines all sensors into a single logical device, "YaInternetometr".

    Methods:
        `__init__`: initializes the sensor, assigns attributes, and links it to the data update coordinator.
        `native_value` (property): returns the current metric value from coordinator.data. Rounding and processing can be added here.
    """

    def __init__(self, coordinator, sensor_type: str, name: str, device_call: str|None, unit: str, icon: str):
        """Initializing the YaInternetometr sensor."""
        super().__init__(coordinator)

        # Metrics
        self.sensor_type = sensor_type
        self._attr_name = name
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"

        # Device class, if specified, for the correct data type in HA
        if device_call:
            self._attr_device_class = device_call

        # General information about "Device" for combining all sensors
        self._attr_device_info = {
            "identifiers": {(DOMAIN, DEVICE_IDENTIFIER)},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
        }

    @property
    def native_value(self):
        """
        Returns the current sensor value from the coordinator.

        Home Assistant uses this property to display the sensor state in the UI, history, and graphs. You can add rounding here, for example:
            ```
            return round(value, 2)
            ```
        """
        return self.coordinator.data.get(self.sensor_type) if self.coordinator.data else None