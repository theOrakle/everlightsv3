"""Constants for the Everlightsv3 online component."""
import logging

from homeassistant.const import EntityCategory
from homeassistant.components.light import LightEntityDescription
from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription

_LOGGER = logging.getLogger(__name__)

DOMAIN = "everlightsv3"

COORDINATOR = "coordinator"

# In Seconds
UPDATE_FREQ = 5

LIGHTS: dict[str, LightEntityDescription] = {
    "led": LightEntityDescription(
        name="Everlights",
        icon="mdi:led-on",
        key="state")
}

SENSORS: dict[str, SensorEntityDescription] = {
    "rssi": SensorEntityDescription(
        name="Signal Strength",
        icon="mdi:signal-variant",
        key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH),
    "lastRequestDate": SensorEntityDescription(
        name="Request Date",
        icon="mdi:update",
        key="lastRequestDate",
        device_class=SensorDeviceClass.DATE),
    "lastResponseDate": SensorEntityDescription(
        name="Response Date",
        icon="mdi:update",
        key="lastResponseDate",
        device_class=SensorDeviceClass.DATE)
}
