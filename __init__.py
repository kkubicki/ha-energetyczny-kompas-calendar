from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_setups(entry, [ "calendar" ] )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok  = await hass.config_entries.async_unload_platforms(entry, [ "calendar" ] )
    return unload_ok
