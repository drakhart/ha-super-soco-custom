from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_DEVICE_NUMBER,
    DATA_MODEL_NAME,
    DOMAIN,
    MANUFACTURER,
)


class SuperSocoCustomEntity(CoordinatorEntity):
    def __init__(self, config_entry, coordinator):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.data.get(DATA_DEVICE_NUMBER))},
            "name": f"{MANUFACTURER} {self.coordinator.data.get(DATA_MODEL_NAME)}",
            "model": self.coordinator.data.get(DATA_MODEL_NAME),
            "manufacturer": MANUFACTURER,
        }
