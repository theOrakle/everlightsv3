"""Sensor platform for everlights."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass
from homeassistant.const import EntityCategory

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
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="snr",
        name="Signal to Noise",
        icon="mdi:sine-wave",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dB",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="lastRequestDate",
        name="Last Request Date",
        icon="mdi:timeline-clock-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="lastResponseDate",
        name="Last Response Time",
        icon="mdi:timeline-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
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
        super().__init__(coordinator,entity_description,serial)
        self.entity_description = entity_description
        self._name = f'{serial} {entity_description.name}'
        self.serial = serial

    @property
    def name(self):
        return self._name

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        desc = self.entity_description
        value = self.coordinator.data[self.serial].get(desc.key)
        if desc.device_class == SensorDeviceClass.TIMESTAMP:
            return dt.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            return value
