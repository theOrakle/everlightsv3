"""Tests for the Everlights API client against a stubbed bridge."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.everlights.api import EverlightsApiClient

HOST = "192.168.1.50"


async def test_410_falls_back_to_status(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Firmware B5010: control API is 410 Gone, only GET /v1 answers."""
    gone = {"error": "gone", "cloud": True}
    aioclient_mock.get(f"http://{HOST}/v1/sequences", json=gone, status=410)
    aioclient_mock.get(f"http://{HOST}/v1/zones", json=gone, status=410)
    aioclient_mock.get(
        f"http://{HOST}/v1",
        json={"zones": [{"serial": "z1", "rssi": -67, "snr": 9}], "cloud": True},
        headers={"Content-Type": "application/json"},
    )
    client = EverlightsApiClient(HOST, async_get_clientsession(hass))
    data = await client.async_get_data()
    assert client.local_control is False
    assert data == {"z1": {"serial": "z1", "rssi": -67, "snr": 9}}
