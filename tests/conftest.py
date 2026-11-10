"""Shared fixtures for the Everlights tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.everlights.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"

SERIAL = "ABC123"

ZONE_DATA = {
    "firmwareVersion": "1.2.3",
    "hardwareVersion": 4,
    "rssi": -61,
    "snr": 9,
    "lastRequestDate": "2026-10-20T12:00:00Z",
    "lastResponseDate": "2026-10-20T12:00:01Z",
    "pattern": ["ff0000"],
    "effects": [],
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow Home Assistant to load the custom integration under test."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return an Everlights config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="192.168.1.50",
        unique_id="192.168.1.50",
        data={CONF_HOST: "192.168.1.50"},
    )


@pytest.fixture
def mock_client() -> Generator[MagicMock]:
    """Patch the Everlights API client everywhere it is constructed."""
    with (
        patch("custom_components.everlights.EverlightsApiClient", autospec=True) as client_cls,
        patch("custom_components.everlights.config_flow.EverlightsApiClient", new=client_cls),
    ):
        client = client_cls.return_value
        client.local_control = True
        client.sequences = [{"alias": "Rainbow", "pattern": ["00ff00"], "effects": []}]
        client.async_get_data = AsyncMock(return_value={SERIAL: dict(ZONE_DATA)})
        client.async_set_sequence = AsyncMock()
        yield client
