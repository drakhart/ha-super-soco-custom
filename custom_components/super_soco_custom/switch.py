import logging

from homeassistant.components.switch import SwitchEntity

from .const import (
    DATA_MODEL_NAME,
    DEFAULT_INTEGER,
    DEFAULT_STRING,
    DOMAIN,
    MANUFACTURER,
    SWITCHES,
)
from .entity import SuperSocoCustomEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    switches = []

    for (
        id,  # pylint: disable=redefined-builtin
        name,
        key,
        condition,
        icon,
        extra_attrs,
    ) in SWITCHES:
        if not key in coordinator.data:
            _LOGGER.debug("Unable to set up switch due to missing data key: %s", key)
        else:
            switches.append(
                SuperSocoCustomSwitch(
                    config_entry,
                    coordinator,
                    id,
                    name,
                    key,
                    condition,
                    icon,
                    extra_attrs,
                )
            )

    async_add_entities(switches)


class SuperSocoCustomSwitch(SuperSocoCustomEntity, SwitchEntity):
    def __init__(
        self,
        config_entry,
        coordinator,
        id,  # pylint: disable=redefined-builtin
        name,
        key,
        condition,
        icon,
        extra_attrs,
    ):
        super().__init__(config_entry, coordinator)
        self._id = id
        self._name = name
        self._key = key
        self._condition = condition
        self._icon = icon
        self._extra_attrs = extra_attrs

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        await self.coordinator.set_switch_state(self._key, True)

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        await self.coordinator.set_switch_state(self._key, False)

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._id}"

    @property
    def translation_key(self):
        return self._id

    @property
    def has_entity_name(self):
        return True

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self.coordinator.data.get(self._key, DEFAULT_INTEGER) == self._condition

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        if type(self._extra_attrs) is dict:
            extra_attrs = {}

            for key, value in self._extra_attrs.items():
                extra_attrs[key] = self.coordinator.data.get(value, DEFAULT_STRING)

            return extra_attrs

        return None
