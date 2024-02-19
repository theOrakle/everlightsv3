"""Light platform for everlights."""
from __future__ import annotations

import homeassistant.util.color as color_util
from homeassistant.components.light import (
    LightEntity, 
    LightEntityDescription,
    LightEntityFeature,
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ColorMode,
)

from .const import DOMAIN
from .coordinator import EverlightsDataUpdateCoordinator
from .entity import EverlightsEntity

ENTITY_DESCRIPTIONS = (
    LightEntityDescription(
        key="pattern",
        name=DOMAIN.capitalize(),
        icon="mdi:led-on",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        EverlightsLight(
            coordinator=coordinator,
            entity_description=entity_description,
            serial=serial
        )
        for entity_description in ENTITY_DESCRIPTIONS
        for serial in coordinator.data
    )


class EverlightsLight(EverlightsEntity, LightEntity):
    """everlights light class."""

    _attr_color_mode = ColorMode.HS
    _attr_supported_color_modes = {ColorMode.HS}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(
        self,
        coordinator: EverlightsDataUpdateCoordinator,
        entity_description: LightEntityDescription,
        serial,
    ) -> None:
        """Initialize the light class."""
        super().__init__(coordinator, serial, entity_description)
        self.entity_description = entity_description
        self.serial = serial
        aliases = []
        for sequence in coordinator.client.sequences:
            aliases.append(sequence["alias"])
        self._attr_effect_list = aliases
        self._attr_effect_list.sort()

    @property
    def is_on(self) -> bool:
        """Return true if the light is on."""
        pattern = self.coordinator.data[self.serial].get(self.entity_description.key)
        state = not(pattern == [])
        if state:
            rgb_color = color_util.rgb_hex_to_rgb_list(pattern[0])
            self._attr_brightness = 255
            self._attr_hs_color = color_util.color_RGB_to_hs(*rgb_color)
            self._attr_rgb_color = rgb_color
        else:
            self._attr_hs_color = None
            self._attr_rgb_color = None
            self._attr_brightness = None
            self._attr_effect = None
        return state

    async def async_turn_on(self, **_: any) -> None:
        """Turn on the light."""
        fx=[]
        effect = _.get(ATTR_EFFECT, self._attr_effect)
        hs_color = _.get(ATTR_HS_COLOR, self._attr_hs_color)
        if hs_color is None:
            hs_color = (0,100)
        rgb_color = color_util.color_hs_to_RGB(hs_color[0],hs_color[1])
        hex_color = [color_util.color_rgb_to_hex(*rgb_color)]
        if effect is not None:
            sequences = self.coordinator.client.sequences
            sequence = [x for x in sequences if "alias" in x and x["alias"]==effect][0]
            hex_color=sequence["pattern"]
            fx=sequence["effects"]
        sequence = {"pattern":hex_color,"effects":fx}
        await self.coordinator.client.async_set_sequence(self.serial, sequence)
        self._attr_brightness = 255
        self._attr_hs_color = hs_color
        self._attr_rgb_color = rgb_color
        self._attr_effect = effect
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: any) -> None:
        """Turn off the light."""
        sequence = {"pattern":[],"effects":[]}
        await self.coordinator.client.async_set_sequence(self.serial, sequence)
        await self.coordinator.async_request_refresh()
