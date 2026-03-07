"""Everlights API Client."""
from __future__ import annotations

import asyncio
import json
import socket
import time
from typing import Any

import aiohttp
import async_timeout

from .const import LOGGER

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
        self._write_lock = asyncio.Lock()
        self._last_write = 0.0

    async def async_load_sequences(self):
        """Get sequences from the API."""
        if self.sequences is None:
            self.sequences = await self._api_wrapper(
                method="get", url=f"http://{self._host}/v1/sequences"
            )

    async def async_get_data(self) -> dict[str, dict[str, Any]]:
        """Get data from the API."""
        data: dict[str, dict[str, Any]] = {}
        await self.async_load_sequences()
        zones = await self._api_wrapper(
            method="get", url=f"http://{self._host}/v1/zones"
        )
        if not isinstance(zones, list):
            raise EverlightsApiClientError(
                f"Unexpected zones payload type: {type(zones).__name__}"
            )
        for zone in zones:
            serial = zone.get("serial")
            if not serial:
                LOGGER.warning("Skipping zone without serial: %s", zone)
                continue
            sequence = await self._api_wrapper(
                method="get", url=f"http://{self._host}/v1/zones/{serial}/sequence"
            )
            zone.pop("serial", None)
            zone.update(sequence)
            data[serial] = zone
        LOGGER.debug(data)
        return data

    async def async_set_sequence(self, serial: str, sequence: dict[str, Any]) -> None:
        """Set data from the API."""
        async with self._write_lock:
            # Bridge can fail when writes are stacked too tightly.
            elapsed = time.monotonic() - self._last_write
            if elapsed < 0.2:
                await asyncio.sleep(0.2 - elapsed)

            last_exception: Exception | None = None
            for attempt in range(1, 4):
                try:
                    await self._api_wrapper(
                        method="post",
                        url=f"http://{self._host}/v1/zones/{serial}/sequence",
                        data=sequence,
                    )
                    self._last_write = time.monotonic()
                    return
                except EverlightsApiClientCommunicationError as exception:
                    last_exception = exception
                    if attempt == 3:
                        break
                    await asyncio.sleep(0.3 * attempt)

            raise last_exception or EverlightsApiClientCommunicationError(
                f"Error setting sequence for zone {serial}"
            )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                async with self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                ) as response:
                    if response.status in (401, 403):
                        raise EverlightsApiClientAuthenticationError(
                            "Invalid credentials",
                        )
                    response.raise_for_status()
                    if response.status == 204:
                        return None

                    response_text = await response.text()
                    if not response_text:
                        return None
                    if "json" in response.content_type:
                        return json.loads(response_text)
                    return response_text

        except asyncio.TimeoutError as exception:
            raise EverlightsApiClientCommunicationError(
                f"Timeout error fetching information from {url}",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise EverlightsApiClientCommunicationError(
                f"Error fetching information from {url}: {exception}",
            ) from exception
        except EverlightsApiClientError:
            raise
        except Exception as exception:  # pylint: disable=broad-except
            raise EverlightsApiClientError(
                f"Unexpected error fetching information from {url}: {exception}"
            ) from exception
