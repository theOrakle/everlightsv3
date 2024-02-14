import pydash
import homeassistant.util.color as color_util
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.core import callback
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from .const import DOMAIN, _LOGGER, LIGHTS

async def async_setup_entry(hass, config, async_add_entities):
    coordinator = hass.data[DOMAIN][config.entry_id]
    entities = []
    for zone in coordinator.devices:
        for field in LIGHTS:
            entities.append(MyLight(coordinator, zone, LIGHTS[field]))
    async_add_entities(entities)

class MyLight(LightEntity):
    _attr_color_mode = ColorMode.HS
    _attr_supported_color_modes = {ColorMode.HS}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(self,coordinator,zone,entity):
        self.coordinator = coordinator
        self.serial = pydash.get(zone,"serial") 
        self.entity = entity
        aliases = []
        for scene in coordinator.scenes:
            aliases.append(scene["alias"])
        self.scenes = coordinator.scenes
        self._name = entity.name
        self._icon = entity.icon
        self._state = pydash.get(self.coordinator.zones[self.serial], self.entity.key)
        self._attributes = {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.serial)},
            manufacturer=DOMAIN,
            model=f"Zone-{self.serial}",
            sw_version=pydash.get(zone,"firmwareVersion"),
            hw_version=pydash.get(zone,"hardwareVersion"),
            name=self.serial)
        self._attr_effect_list = aliases
        self._error_reported = False

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.serial}_{self._name}"

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

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
    
    async def async_turn_on(self, **kwargs) -> None:
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
        await self.coordinator.set_sequence(self.serial,seq)
        self._state = "on"
        self._attr_brightness = 255
        self._attr_hs_color = hs_color 
        self._attr_rgb_color = rgb_color 
        self._attr_effect = effect
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        seq = {"pattern":[],"effects":[]}
        await self.coordinator.set_sequence(self.serial,seq)
        self._state = "off"
        self._attr_hs_color = None
        self._attr_rgb_color = None
        self._attr_brightness = None
        self._attr_effect = None
        await self.coordinator.async_request_refresh()

    async def async_update(self):
        self._state = pydash.get(self.coordinator.zones[self.serial], self.entity.key)
        if self._state == "on":
            pattern = pydash.get(self.coordinator.zones[self.serial], "sequence.pattern")
            hex_color = pydash.get(pattern,"0")
            rgb_color = color_util.rgb_hex_to_rgb_list(hex_color)
            self._attr_brightness = 255
            self._attr_hs_color = color_util.color_RGB_to_hs(*rgb_color) 
            self._attr_rgb_color = rgb_color 
        else:
            self._attr_hs_color = None
            self._attr_rgb_color = None
            self._attr_brightness = None
            self._attr_effect = None
