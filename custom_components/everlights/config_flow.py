"""Adds config flow for Everlights."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    EverlightsApiClient,
    EverlightsApiClientAuthenticationError,
    EverlightsApiClientCommunicationError,
    EverlightsApiClientError,
)
from .const import DOMAIN, LOGGER


class EverlightsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Everlights."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(
                    host=user_input[CONF_HOST],
                )
            except EverlightsApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except EverlightsApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except EverlightsApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_connection(self, host: str) -> None:
        """Validate host."""
        client = EverlightsApiClient(
            host=host,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
