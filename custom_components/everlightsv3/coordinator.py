from __future__ import annotations

import aiohttp
import json
import pydash
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator, 
    UpdateFailed
)
from .const import DOMAIN, _LOGGER, UPDATE_FREQ

class EverlightsCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, host):
        self.url = f'http://{host}/v1'
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_FREQ)
        )

    async def _async_update_data(self):
        self.sequences = {}
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(self.url+"/sequences") as r:
                    self.scenes = await r.json()
            async with aiohttp.ClientSession() as s:
                async with s.get(self.url) as r:
                    bridge = await r.json()
            self.bridge = bridge["serial"]
            self.devices = bridge["zones"]
            for device in self.devices:
                zone = pydash.get(device,"serial")
                async with aiohttp.ClientSession() as s:
                    async with s.get(f"{self.url}/zones/{zone}/sequence") as r:
                        seq = await r.json()
                self.sequences[zone]=seq
        except Exception as err:
            _LOGGER.error(f"Error communicating with API: {err}")
            raise UpdateFailed(err)

    async def set_sequence(self, zone, seq):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(f"{self.url}/zones/{zone}/sequence",json=seq) as r:
                    req = await r.json()
        except Exception as err:
            _LOGGER.error(f"Error communicating with API: {err}")
            raise UpdateFailed(err)
