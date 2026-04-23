import logging
from typing import cast

from homeassistant.components.switch import SwitchEntity

from .const import (
    DEFAULT_INTEGER,
    DEFAULT_STRING,
    DOMAIN,
    SWITCHES,
)
from .coordinator import VmotoDataUpdateCoordinator
from .entity import VmotoEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    switches = []

    for (
        switch_id,
        key,
        condition,
        icon,
        extra_attrs,
    ) in SWITCHES:
        if key not in coordinator.data:
            _LOGGER.debug("Unable to set up switch due to missing data key: %s", key)
        else:
            switches.append(
                VmotoSwitch(
                    config_entry,
                    coordinator,
                    switch_id,
                    key,
                    condition,
                    icon,
                    extra_attrs,
                )
            )

    async_add_entities(switches)


class VmotoSwitch(VmotoEntity, SwitchEntity):
    def __init__(
        self,
        config_entry,
        coordinator,
        switch_id,
        key,
        condition,
        icon,
        extra_attrs,
    ):
        super().__init__(config_entry, coordinator)
        self._id = switch_id
        self._key = key
        self._condition = condition
        self._icon = icon
        self._extra_attrs = extra_attrs

    async def async_turn_on(self, **kwargs):
        await cast("VmotoDataUpdateCoordinator", self.coordinator).set_switch_state(
            self._key, True
        )

    async def async_turn_off(self, **kwargs):
        await cast("VmotoDataUpdateCoordinator", self.coordinator).set_switch_state(
            self._key, False
        )

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
    def is_on(self):
        return self.coordinator.data.get(self._key, DEFAULT_INTEGER) == self._condition

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        if isinstance(self._extra_attrs, dict):
            extra_attrs = {}

            for key, value in self._extra_attrs.items():
                extra_attrs[key] = self.coordinator.data.get(value, DEFAULT_STRING)

            return extra_attrs

        return None
