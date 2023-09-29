"""Constants for the Everlightsv3 online component."""
import logging

from homeassistant.const import Platform
from homeassistant.components.light import LightDeviceClass, LightEntityDescription

_LOGGER = logging.getLogger(__name__)

DOMAIN = "everlightsv3"

ICON = 'mdi:led-on'

HOST = "api.mill.com"
URL = f"https://{HOST}/app/v1"

PLATFORMS = [
    Platform.LIGHT
]
LIGHTS: dict[str, SensorEntityDescription] = {
    "led": LightEntityDescription(
        name="Everlights",
        icon=ICON,
        key="data.attributes.massInBucket")
}
