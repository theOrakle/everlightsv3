from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_HOSTS
from .exceptions import ApiException
from .const import DOMAIN, _LOGGER

DATA_SCHEMA = vol.Schema(
  {
    vol.Required(CONF_HOSTS): str
  }
)

async def validate_input(hass: core.HomeAssistant, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://"+data[CONF_HOSTS]+"/v1") as r:
                results = await r.json()
    except:
        _LOGGER.error('Troubles talking to the API')
        raise ApiException()
    if r.status == 200:
        return data
    else:
        raise ApiException()

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=user_input[CONF_HOSTS], data=info)
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )   
