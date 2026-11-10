"""Tests for Everlights setup, unload and entities."""
from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.everlights.api import (
    EverlightsApiClientAuthenticationError,
    EverlightsApiClientCommunicationError,
)
from custom_components.everlights.const import DOMAIN

from .conftest import SERIAL


async def test_setup_and_unload(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """The entry loads, creates the device and entities, and unloads cleanly."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED

    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, SERIAL), mock_config_entry.entry_id
    )
    assert device is not None
    assert device.manufacturer == "Everlights"
    assert device.name == SERIAL

    light = hass.states.get("light.abc123_everlights")
    assert light is not None and light.state == "on"
    assert light.attributes["effect_list"] == ["Rainbow"]
    assert hass.states.get("sensor.abc123_signal_strength").state == "-61"

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_light_controls_call_api(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """Turning the light off and on forwards a sequence to the bridge."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        "light", "turn_off", {"entity_id": "light.abc123_everlights"}, blocking=True
    )
    mock_client.async_set_sequence.assert_awaited_with(
        SERIAL, {"pattern": [], "effects": []}
    )

    await hass.services.async_call(
        "light",
        "turn_on",
        {"entity_id": "light.abc123_everlights", "effect": "Rainbow"},
        blocking=True,
    )
    mock_client.async_set_sequence.assert_awaited_with(
        SERIAL, {"pattern": ["00ff00"], "effects": []}
    )


async def test_legacy_entry_gets_unique_id(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """Entries created before unique IDs existed are migrated on setup."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "10.0.0.5"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    assert entry.unique_id == "10.0.0.5"


async def test_setup_retries_when_bridge_unreachable(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """A connection failure at setup is retried, not a hard error."""
    mock_client.async_get_data.side_effect = EverlightsApiClientCommunicationError("down")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_rejected_request_marks_setup_error(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """An authentication rejection stops setup (the bridge has no login to redo)."""
    mock_client.async_get_data.side_effect = EverlightsApiClientAuthenticationError("bad")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR


async def test_local_control_removed_keeps_sensors(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """Firmware B5010+ (410 Gone): setup succeeds, sensors work, light unavailable."""
    mock_client.local_control = False
    mock_client.sequences = None
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert hass.states.get("light.abc123_everlights").state == "unavailable"
    assert hass.states.get("sensor.abc123_signal_strength").state == "-61"
    issue_id = f"local_control_removed_{mock_config_entry.entry_id}"
    assert ir.async_get(hass).async_get_issue(DOMAIN, issue_id) is not None
