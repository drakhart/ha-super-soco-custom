from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    pass


class LoginCodeFailed(HomeAssistantError):
    pass


class BindFailed(HomeAssistantError):
    pass
