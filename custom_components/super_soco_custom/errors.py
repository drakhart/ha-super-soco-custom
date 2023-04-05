from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    pass


class InvalidAuth(HomeAssistantError):
    pass
