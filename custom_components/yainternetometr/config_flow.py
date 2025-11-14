import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class YaInternetometrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Config Flow for YaInternetometr integration.

    This class allows the user to add integrations through the Home Assistant UI without having to edit configuration.yaml.

    Inherits:
        `config_entries.ConfigFlow`: base class for creating interactive configuration flows in Home Assistant.

    Attributes:
        `VERSION` (int): Configuration structure version. Allows you to manage migration of configurations when changing the integration.
    """

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="YaInternetometr", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})
        )