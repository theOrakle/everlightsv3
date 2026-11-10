"""DataUpdateCoordinator for everlights."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    EverlightsApiClient,
    EverlightsApiClientAuthenticationError,
    EverlightsApiClientError,
)
from .const import DOMAIN, LOGGER

type EverlightsConfigEntry = ConfigEntry[EverlightsDataUpdateCoordinator]


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class EverlightsDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Class to manage fetching data from the API."""

    config_entry: EverlightsConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: EverlightsConfigEntry,
        client: EverlightsApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        self._control_available: bool | None = None
        self._issue_id = f"local_control_removed_{config_entry.entry_id}"
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Update data via library."""
        was_available = self._control_available
        try:
            data = await self.client.async_get_data()
        except EverlightsApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except EverlightsApiClientError as exception:
            raise UpdateFailed(exception) from exception
        self._control_available = self.client.local_control
        if self._control_available:
            ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
            if was_available is False:
                # Control is back: reload so the light rebuilds its effect list.
                self.hass.config_entries.async_schedule_reload(
                    self.config_entry.entry_id
                )
        else:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                self._issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key="local_control_removed",
                learn_more_url="https://github.com/theOrakle/everlightsv3/issues/4",
            )
        return data
