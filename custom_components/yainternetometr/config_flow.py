from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

import voluptuous
from typing import Any
from .const import DOMAIN, DEFAULT_NAME

class YaInternetometrConfigFlow(ConfigFlow, domain=DOMAIN):
    """
    Config Flow for YaInternetometr integration.

    This class allows the user to add integrations through the Home Assistant UI without having to edit configuration.yaml.

    Inherits:
        `config_entries.ConfigFlow`: base class for creating interactive configuration flows in Home Assistant.

    Attributes:
        `VERSION` (int): Configuration structure version. Allows you to manage migration of configurations when changing the integration.
    """

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
    
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_NAME, data={})

        return self.async_show_form(step_id="user", data_schema=voluptuous.Schema({}))