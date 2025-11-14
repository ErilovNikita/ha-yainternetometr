# custom_components/yainternetometr/sensors.py

from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SENSOR_PING, SENSOR_DOWNLOAD, SENSOR_UPLOAD, SCAN_INTERVAL

from yaspeedtest.client import YaSpeedTest

async def fetch_speedtest_data():
    try:
        ya = await YaSpeedTest().create()
        result = await ya.run()
        return {
            SENSOR_PING: result.ping_ms,
            SENSOR_DOWNLOAD: result.download_mbps,
            SENSOR_UPLOAD: result.upload_mbps,
        }
    except Exception as e:
        raise UpdateFailed(f"Error fetching speed test: {e}")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up sensors via DataUpdateCoordinator."""
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER := hass.logger,
        name=DOMAIN,
        update_method=fetch_speedtest_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    await coordinator.async_refresh()

    sensors = [
        YaSpeedSensor(coordinator, SENSOR_PING, "Ping", "ms"),
        YaSpeedSensor(coordinator, SENSOR_DOWNLOAD, "Download", "Mbps"),
        YaSpeedSensor(coordinator, SENSOR_UPLOAD, "Upload", "Mbps"),
    ]

    async_add_entities(sensors)

class YaSpeedSensor(SensorEntity):
    """Sensor для одной метрики speedtest."""

    def __init__(self, coordinator, sensor_type, name, unit):
        self.coordinator = coordinator
        self.sensor_type = sensor_type
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_state = None

    @property
    def native_value(self):
        return self.coordinator.data.get(self.sensor_type) if self.coordinator.data else None

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()