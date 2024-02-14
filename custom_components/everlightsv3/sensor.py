import pydash
from homeassistant.helpers.entity import Entity, DeviceInfo
from .const import DOMAIN, _LOGGER, SENSORS
from .coordinator import MyCoordinator

async def async_setup_entry(hass, config, async_add_entities):

    coordinator = hass.data[DOMAIN][config.entry_id]
    entities = []
    for zone in coordinator.devices:
        for field in SENSORS:
            entities.append(MySensor(coordinator, zone, SENSORS[field]))
    async_add_entities(entities)

class MySensor(Entity):

    def __init__(self,coordinator,zone,entity):
        self.coordinator = coordinator
        self.serial = pydash.get(zone,"serial") 
        self.entity = entity
        aliases = []
        self._name = entity.name
        self._icon = entity.icon
        self._device_class = entity.device_class
        self._state = pydash.get(self.coordinator.diags[self.serial], self.entity.key)
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
    def device_class(self):
        return self._device_class

    @property
    def state(self):
        return self._state

    @property
    def state_attributes(self):
        return self._attributes

    async def async_update(self):
        self._state = pydash.get(self.coordinator.diags[self.serial], self.entity.key)
