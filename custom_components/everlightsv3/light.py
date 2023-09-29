"""

"""
from __future__ import annotations

import requests
import json
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import homeassistant.util.color as color_util
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.const import CONF_HOSTS
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)

_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = 'Everlights'
UPDATES = timedelta(seconds=5)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOSTS): vol.All(cv.ensure_list, [cv.string])
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    lights = []
    for ipaddr in config[CONF_HOSTS]:
        base_url = f'http://{ipaddr}/v1'
        bridge = requests.get(base_url).json()
        scenes = requests.get(base_url+'/sequences').json()
        for zone in bridge["zones"]:
            status = "on" if f'{zone["active"]}'=='True' else "off"
            lights.append(EverLightsLight(hass, base_url, zone["serial"], status, scenes))
    add_entities(lights)

class EverLightsLight(LightEntity):

    _attr_color_mode = ColorMode.HS
    _attr_supported_color_modes = {ColorMode.HS}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(self,hass,url,zone,status,scenes):
        aliases = []
        for scene in scenes:
            aliases.append(scene["alias"])
        self.hass = hass
        self._state = status
        self._attributes = {}
        self.url = url 
        self.zone = zone
        self.scenes = scenes
        self._attr_effect_list = aliases
        self._error_reported = False
        self.updated = False
        self.update()

    @property
    def unique_id(self):
        return f'everlights_{self.zone}'

    @property
    def name(self):
        return f'everlights_{self.zone}'

    @property
    def icon(self):
        return 'mdi:led-on'

    @property
    def state(self):
        return self._state

    @property
    def state_attributes(self):
        self._attributes["brightness"] = self._attr_brightness
        self._attributes["hs_color"] = self._attr_hs_color
        self._attributes["rgb_color"] = self._attr_rgb_color
        self._attributes["effect"] = self._attr_effect
        return self._attributes

    @property
    def is_on(self) -> bool:
        return self._state == "on" 
    
    def turn_on(self, **kwargs) -> None:
        fx=[]
        effect = kwargs.get(ATTR_EFFECT, self._attr_effect)
        hs_color = kwargs.get(ATTR_HS_COLOR, self._attr_hs_color)
        if hs_color is None:
            hs_color = (0,100)
        rgb_color = color_util.color_hs_to_RGB(hs_color[0],hs_color[1])
        hex_color = [color_util.color_rgb_to_hex(*rgb_color)]
        if effect is not None:
            scene = [x for x in self.scenes if "alias" in x and x["alias"]==effect][0]
            hex_color=scene["pattern"]
            fx=scene["effects"]
        seq = {"pattern":hex_color,"effects":fx}
        req = requests.post(f"{self.url}/zones/{self.zone}/sequence",json=seq)
        self._state = "on"
        self._attr_brightness = 255
        self._attr_hs_color = hs_color 
        self._attr_rgb_color = rgb_color 
        self._attr_effect = effect
        self.updated = True
        self.update()

    def turn_off(self) -> None:
        seq = {"pattern":[],"effects":[]}
        req = requests.post(f"{self.url}/zones/{self.zone}/sequence",json=seq)
        self._state = "off"
        self._attr_hs_color = None
        self._attr_rgb_color = None
        self._attr_brightness = None
        self._attr_effect = None
        self.updated = True

    @Throttle(UPDATES)
    def update(self):
        if not self.updated:
            try: 
                active = requests.get(f"{self.url}/zones/{self.zone}").json()["active"]
                self._state = "on" if f'{active}'=='True' else "off"
            except:
                self._state = "unknown"
                _LOGGER.error("Failed to communicate to the API")
        if self._state == "on":
            try:
                hex_color = requests.get(f"{self.url}/zones/{self.zone}/sequence").json()["pattern"][0]
                rgb_color = color_util.rgb_hex_to_rgb_list(hex_color)
                self._attr_brightness = 255
                self._attr_hs_color = color_util.color_RGB_to_hs(*rgb_color) 
                self._attr_rgb_color = rgb_color 
            except:
                self._attr_brightness = None
                self._attr_hs_color = None
                self._attr_rgb_color = None
                self._attr_effect = None
                self._state = "off"
                _LOGGER.error("Failed to communicate to the API")
        self.updated = False
