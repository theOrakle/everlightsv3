"""EverlightsEntity class."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION
from .coordinator import EverlightsDataUpdateCoordinator


class EverlightsEntity(CoordinatorEntity):
    """EverlightsEntity class."""

    def __init__(
        self,
        coordinator: EverlightsDataUpdateCoordinator,
        entity_description,
        serial: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{serial}_{entity_description.key}"
        zone_data: dict[str, Any] = coordinator.data.get(serial, {})
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=serial,
            model=f"Integration {VERSION}",
            manufacturer=DOMAIN.capitalize(),
            sw_version=zone_data.get("firmwareVersion"),
            hw_version=zone_data.get("hardwareVersion"),
        )
