"""Adds config flow for Everlights."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    EverlightsApiClient,
    EverlightsApiClientAuthenticationError,
    EverlightsApiClientCommunicationError,
    EverlightsApiClientError,
)
from .const import DOMAIN, LOGGER


def _host_schema(default: str | None = None) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=default): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
        }
    )


class EverlightsFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Everlights."""

    VERSION = 1
    _local_control = True

    async def _validate(self, host: str) -> str | None:
        """Test the bridge and return a flow error key, or None when it works."""
        try:
            await self._test_connection(host=host)
        except EverlightsApiClientAuthenticationError as exception:
            LOGGER.warning(exception)
            return "invalid_auth"
        except EverlightsApiClientCommunicationError as exception:
            LOGGER.error(exception)
            return "cannot_connect"
        except EverlightsApiClientError as exception:
            LOGGER.exception(exception)
            return "unknown"
        return None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            error = await self._validate(host)
            if error is None and not self._local_control:
                # Nothing could be controlled, so don't add a new bridge like this.
                error = "local_control_removed"
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(host.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=host,
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_host_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Let an existing entry's bridge host be edited (e.g. after a DHCP change)."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if error := await self._validate(host):
                errors["base"] = error
            else:
                if host.lower() != reconfigure_entry.unique_id:
                    # Moving to a host another entry already uses must not merge them.
                    await self.async_set_unique_id(host.lower())
                    self._abort_if_unique_id_configured()
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    unique_id=host.lower(),
                    title=host,
                    data_updates={CONF_HOST: host},
                    reason="reconfigure_successful",
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_host_schema(default=reconfigure_entry.data.get(CONF_HOST)),
            errors=errors,
        )

    async def _test_connection(self, host: str) -> None:
        """Validate host."""
        client = EverlightsApiClient(
            host=host,
            session=async_get_clientsession(self.hass),
        )
        await client.async_get_data()
        self._local_control = client.local_control
