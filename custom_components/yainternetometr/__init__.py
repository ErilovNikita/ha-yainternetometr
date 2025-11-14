# custom_components/yainternetometr/__init__.py

from homeassistant.core import HomeAssistant

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up is not used for config flow."""
    return True

async def async_setup_entry(hass, entry):
    """Set up the integration from config flow."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True