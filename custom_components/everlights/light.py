"""Light platform for everlights."""
from __future__ import annotations

from typing import Any

import homeassistant.util.color as color_util
from homeassistant.components.light import (
    LightEntity,
    LightEntityDescription,
    LightEntityFeature,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ColorMode,
)

from .const import DOMAIN, LOGGER
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
        super().__init__(coordinator, entity_description, serial)
        self.entity_description = entity_description
        self.serial = serial
        self._name = f'{serial} {entity_description.name}'
        self._sequence_by_alias: dict[str, dict[str, Any]] = {
            sequence["alias"]: sequence
            for sequence in coordinator.client.sequences
            if "alias" in sequence
        }
        self._attr_effect_list = list(self._sequence_by_alias)
        self._attr_effect_list.sort()

    @property
    def name(self):
        return self._name


    @property
    def is_on(self) -> bool:
        """Return true if the light is on."""
        desc = self.entity_description
        pattern = self.coordinator.data[self.serial].get(desc.key)
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

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        fx = []
        effect = kwargs.get(ATTR_EFFECT, self._attr_effect)
        hs_color = kwargs.get(ATTR_HS_COLOR, self._attr_hs_color)
        if hs_color is None:
            hs_color = (0, 100)
        rgb_color = color_util.color_hs_to_RGB(hs_color[0], hs_color[1])
        hex_color = [color_util.color_rgb_to_hex(*rgb_color)]
        if effect is not None:
            sequence = self._sequence_by_alias.get(effect)
            if sequence is None:
                LOGGER.warning("Unknown effect '%s' for zone %s", effect, self.serial)
                effect = None
            else:
                hex_color = sequence.get("pattern", hex_color)
                fx = sequence.get("effects", fx)
        sequence = {"pattern": hex_color, "effects": fx}
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
        self._attr_hs_color = None
        self._attr_rgb_color = None
        self._attr_brightness = None
        self._attr_effect = None
        await self.coordinator.async_request_refresh()
