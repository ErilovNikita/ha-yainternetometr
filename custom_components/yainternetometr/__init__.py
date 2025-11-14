# custom_components/yainternetometr/__init__.py

from homeassistant.core import HomeAssistant

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up is not used for config flow."""
    return True

async def async_setup_entry(hass, entry):
    """Set up the integration from config flow."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True