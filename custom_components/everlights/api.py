"""Everlights API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

class EverlightsApiClientError(Exception):
    """Exception to indicate a general API error."""


class EverlightsApiClientCommunicationError(
    EverlightsApiClientError
):
    """Exception to indicate a communication error."""


class EverlightsApiClientAuthenticationError(
    EverlightsApiClientError
):
    """Exception to indicate an authentication error."""


class EverlightsApiClient:
    """Everlights API Client."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Everlights API Client."""
        self._host = host
        self._session = session
        self.sequences = None

    async def async_load_sequences(self):
        """Get sequences from the API."""
        if self.sequences is None:
            self.sequences = await self._api_wrapper(
                method="get", url=f"http://{self._host}/v1/sequences"
            )

    async def async_get_data(self) -> any:
        """Get data from the API."""
        await self.async_load_sequences()
        data = {}
        zones = await self._api_wrapper(
            method="get", url=f"http://{self._host}/v1/zones"
        )
        for zone in zones:
            serial = zone.get("serial")
            sequence = await self._api_wrapper(
                method="get", url=f"http://{self._host}/v1/zones/{serial}/sequence"
            )
            del zone["serial"]
            zone.update(sequence)
            data[serial] = zone
        return data

    async def async_set_sequence(self, serial, sequence: str) -> any:
        """Set data from the API."""
        return await self._api_wrapper(
            method="post",
            url=f"http://{self._host}/v1/zones/{serial}/sequence",
            data=sequence
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise EverlightsApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise EverlightsApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise EverlightsApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise EverlightsApiClientError(
                "Something really wrong happened!"
            ) from exception
