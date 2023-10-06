"""Constants for the Everlightsv3 online component."""
import logging

from homeassistant.const import Platform
from homeassistant.components.light import LightEntityDescription

_LOGGER = logging.getLogger(__name__)

DOMAIN = "everlightsv3"

COORDINATOR = "coordinator"

# In Seconds
UPDATE_FREQ = 5

PLATFORMS = [
    Platform.LIGHT
]

LIGHTS: dict[str, LightEntityDescription] = {
    "led": LightEntityDescription(
        name="Everlights",
        icon="mdi:led-on",
        key="active")
}
