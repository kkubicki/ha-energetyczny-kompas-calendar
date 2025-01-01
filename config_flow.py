from homeassistant import config_entries
#import voluptuous as vol
from .const import DOMAIN

class EnergetycznyKompasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energetyczny Kompas."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Check if an instance already exists
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # Create the configuration entry
            return self.async_create_entry(title="Energetyczny Kompas", data={})

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
