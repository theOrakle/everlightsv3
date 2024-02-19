"""Sensor platform for everlights."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass

from .const import DOMAIN
from .coordinator import EverlightsDataUpdateCoordinator
from .entity import EverlightsEntity

from datetime import datetime as dt

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="rssi",
        name="Signal Strength",
        icon="mdi:signal-variant",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
    ),
    SensorEntityDescription(
        key="snr",
        name="Signal to Noise",
        icon="mdi:sine-wave",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dB",
    ),
    SensorEntityDescription(
        key="lastRequestDate",
        name="Last Request Date",
        icon="mdi:timeline-clock-outline",
        device_class=SensorDeviceClass.DATE,
    ),
    SensorEntityDescription(
        key="lastResponseDate",
        name="Last Response Time",
        icon="mdi:timeline-clock",
        device_class=SensorDeviceClass.DATE,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        EverlightsSensor(
            coordinator=coordinator,
            entity_description=entity_description,
            serial=serial
        )
        for entity_description in ENTITY_DESCRIPTIONS
        for serial in coordinator.data
    )


class EverlightsSensor(EverlightsEntity, SensorEntity):
    """everlights Sensor class."""

    def __init__(
        self,
        coordinator: EverlightsDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        serial,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator,serial,entity_description)
        self.entity_description = entity_description
        self.serial = serial

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        value = self.coordinator.data[self.serial].get(self.entity_description.key)
        if self.entity_description.device_class == SensorDeviceClass.DATE:
            return dt.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            return value