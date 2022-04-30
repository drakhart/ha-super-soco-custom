import logging
import voluptuous as vol

from aiohttp import ClientResponseError, ServerTimeoutError

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    CONF_PASSWORD,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    CONFIG_FLOW_VERSION,
    DEFAULT_ENABLE_ALTITUDE_ENTITY,
    DEFAULT_ENABLE_REVERSE_GEOCODING_ENTITY,
    DEFAULT_ENABLE_LAST_TRIP_ENTITIES,
    DEFAULT_ENABLE_LAST_WARNING_ENTITY,
    DEFAULT_STRING,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
    ERROR_ALREADY_CONFIGURED,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
    ERROR_UNKNOWN,
    MAX_UPDATE_INTERVAL_MINUTES,
    MIN_UPDATE_INTERVAL_MINUTES,
    NAME,
    OPT_EMAIL,
    OPT_ENABLE_ALTITUDE_ENTITY,
    OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
    OPT_ENABLE_LAST_TRIP_ENTITIES,
    OPT_ENABLE_LAST_WARNING_ENTITY,
    OPT_UPDATE_INTERVAL,
    PHONE_PREFIXES,
)
from .super_soco_api import SuperSocoAPI

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = CONFIG_FLOW_VERSION
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self._errors = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        self._errors = {}

        if self._async_current_entries():
            return self.async_abort(reason=ERROR_ALREADY_CONFIGURED)

        if user_input is not None:
            try:
                await self._test_credentials(
                    user_input[CONF_PHONE_PREFIX],
                    user_input[CONF_PHONE_NUMBER],
                    user_input[CONF_PASSWORD],
                )

                return self.async_create_entry(title=NAME, data=user_input)
            except CannotConnect:
                self._errors["base"] = ERROR_CANNOT_CONNECT
            except InvalidAuth:
                self._errors["base"] = ERROR_INVALID_AUTH
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                self._errors["base"] = ERROR_UNKNOWN

            return await self._show_config_form(user_input)

        # Provide defaults for form
        user_input = {}
        user_input[CONF_PHONE_PREFIX] = None
        user_input[CONF_PHONE_NUMBER] = None
        user_input[CONF_PASSWORD] = None

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SuperSocoCustomOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PHONE_PREFIX, default=user_input[CONF_PHONE_PREFIX]
                    ): vol.In(PHONE_PREFIXES),
                    vol.Required(
                        CONF_PHONE_NUMBER, default=user_input[CONF_PHONE_NUMBER]
                    ): int,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(
        self, phone_prefix: int, phone_number: int, password: str
    ) -> bool:
        try:
            session = async_create_clientsession(self.hass)
            client = SuperSocoAPI(session, phone_prefix, phone_number, password)

            await client.login()

            return True
        except ServerTimeoutError:
            raise CannotConnect
        except ClientResponseError as error:
            if error.status == 400:
                raise InvalidAuth
            else:
                raise error


class SuperSocoCustomOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.options.update(user_input)

            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        OPT_UPDATE_INTERVAL,
                        default=self.options.get(
                            OPT_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES
                        ),
                    ): selector.selector(
                        {
                            "number": {
                                "min": MIN_UPDATE_INTERVAL_MINUTES,
                                "max": MAX_UPDATE_INTERVAL_MINUTES,
                            }
                        }
                    ),
                    vol.Required(
                        OPT_ENABLE_LAST_WARNING_ENTITY,
                        default=self.options.get(
                            OPT_ENABLE_LAST_WARNING_ENTITY,
                            DEFAULT_ENABLE_LAST_WARNING_ENTITY,
                        ),
                    ): selector.selector({"boolean": {}}),
                    vol.Required(
                        OPT_ENABLE_LAST_TRIP_ENTITIES,
                        default=self.options.get(
                            OPT_ENABLE_LAST_TRIP_ENTITIES,
                            DEFAULT_ENABLE_LAST_TRIP_ENTITIES,
                        ),
                    ): selector.selector({"boolean": {}}),
                    vol.Required(
                        OPT_ENABLE_ALTITUDE_ENTITY,
                        default=self.options.get(
                            OPT_ENABLE_ALTITUDE_ENTITY, DEFAULT_ENABLE_ALTITUDE_ENTITY
                        ),
                    ): selector.selector({"boolean": {}}),
                    vol.Required(
                        OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
                        default=self.options.get(
                            OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
                            DEFAULT_ENABLE_REVERSE_GEOCODING_ENTITY,
                        ),
                    ): selector.selector({"boolean": {}}),
                    vol.Optional(
                        OPT_EMAIL,
                        default=self.options.get(OPT_EMAIL, DEFAULT_STRING),
                    ): selector.selector({"text": {}}),
                }
            ),
        )

    async def _update_options(self):
        return self.async_create_entry(title=NAME, data=self.options)


class CannotConnect(HomeAssistantError):
    pass


class InvalidAuth(HomeAssistantError):
    pass
