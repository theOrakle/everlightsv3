import pydash
import homeassistant.util.color as color_util
from homeassistant.const import CONF_HOST
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
from .const import DOMAIN, COORDINATOR, _LOGGER, LIGHTS
from .coordinator import EverlightsCoordinator

async def async_setup_entry(hass, config, async_add_entities):

    host = config.data[CONF_HOST]
    coordinator = EverlightsCoordinator(hass, host)
    await coordinator.async_config_entry_first_refresh()
    entities = []
    for zone in coordinator.devices:
        for field in LIGHTS:
            entities.append(EverlightsLight(coordinator, zone, LIGHTS[field]))
    async_add_entities(entities)

class EverlightsLight(LightEntity):

    _attr_color_mode = ColorMode.HS
    _attr_supported_color_modes = {ColorMode.HS}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(self,coordinator,zone,entity):
        self.coordinator = coordinator
        self.zone = zone
        self.entity = entity
        aliases = []
        for scene in coordinator.scenes:
            aliases.append(scene["alias"])
        self.scenes = coordinator.scenes
        self._name = entity.name
        self.serial = pydash.get(self.zone,"serial") 
        self._unique_id = f"{DOMAIN}_{self.serial}_{entity.name}"
        self._icon = entity.icon
        active = pydash.get(self.zone, self.entity.key)
        self._state = "on" if active else "off"
        self._attributes = {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.serial)},
            manufacturer=DOMAIN,
            model=pydash.get(self.zone,"hardwareVersion"),
            name=self.serial)
        self.zone = zone
        self._attr_effect_list = aliases
        self._error_reported = False

    @property
    def unique_id(self):
        return self._unique_id

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
        active = pydash.get(self.zone, self.entity.key)
        self._state = "on" if active else "off"
        if self._state == "on":
            pattern = pydash.get(self.coordinator.sequences[self.serial], "pattern")
            hex_color = pydash.get(pattern,"0")
            rgb_color = color_util.rgb_hex_to_rgb_list(hex_color)
            self._attr_brightness = 255
            self._attr_hs_color = color_util.color_RGB_to_hs(*rgb_color) 
            self._attr_rgb_color = rgb_color 
        self.async_write_ha_state()
