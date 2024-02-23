"""EverlightsEntity class."""
from __future__ import annotations

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
        serial, 
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{serial}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=serial,
            model=f"Integration {VERSION}",
            manufacturer=DOMAIN.capitalize(),
            sw_version=coordinator.data[serial].get("firmwareVersion"),
            hw_version=coordinator.data[serial].get("hardwareVersion"),
        )
