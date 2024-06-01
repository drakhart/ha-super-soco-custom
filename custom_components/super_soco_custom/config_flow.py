import logging
import voluptuous as vol

from aiohttp import ClientResponseError, ClientSession, ServerTimeoutError

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    APP_NAMES,
    CONF_APP_NAME,
    CONF_LOGIN_CODE,
    CONF_PASSWORD,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    CONF_TOKEN,
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
    SUPER_SOCO,
)
from .errors import CannotConnect, InvalidAuth
from .super_soco_api import SuperSocoAPI
from .vmoto_soco_api import VmotoSocoAPI

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = CONFIG_FLOW_VERSION
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        self._errors = {}
        self._session = None
        self._client = None
        self._reauth_entry = None
        self._user_input = {
            CONF_APP_NAME: SUPER_SOCO,
            CONF_PHONE_PREFIX: list(PHONE_PREFIXES.keys())[0],
            CONF_PHONE_NUMBER: None,
            CONF_PASSWORD: None,
            CONF_LOGIN_CODE: None,
        }

    async def async_step_reauth(self, user_input=None) -> FlowResult:
        self._errors = {}
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None) -> FlowResult:
        if self._async_current_entries() and not self._reauth_entry:
            return self.async_abort(reason=ERROR_ALREADY_CONFIGURED)

        if user_input:
            self._user_input.update(user_input)

        errors = self._errors
        self._errors = {}

        return self.async_show_form(
            step_id="app",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_APP_NAME, default=self._user_input[CONF_APP_NAME]
                    ): vol.In(APP_NAMES),
                    vol.Required(
                        CONF_PHONE_PREFIX, default=self._user_input[CONF_PHONE_PREFIX]
                    ): vol.In(PHONE_PREFIXES),
                    vol.Required(
                        CONF_PHONE_NUMBER, default=self._user_input[CONF_PHONE_NUMBER]
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_app(self, user_input=None) -> FlowResult:
        if user_input:
            self._user_input.update(user_input)

        errors = self._errors
        self._errors = {}

        if self._user_input[CONF_APP_NAME] == SUPER_SOCO:
            return self.async_show_form(
                step_id="login",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_PASSWORD, default=self._user_input[CONF_PASSWORD]
                        ): str,
                    }
                ),
                errors=errors,
            )

        try:
            await self._get_login_code()

            return self.async_show_form(
                step_id="login",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_LOGIN_CODE): str,
                    }
                ),
                errors=errors,
            )
        except CannotConnect:
            self._errors["base"] = ERROR_CANNOT_CONNECT
        except InvalidAuth:
            self._errors["base"] = ERROR_INVALID_AUTH
        except Exception as error:  # pylint: disable=broad-exception-caught
            _LOGGER.exception(error)
            self._errors["base"] = ERROR_UNKNOWN

        return await self.async_step_user(user_input)

    async def async_step_login(self, user_input=None) -> FlowResult:
        if user_input:
            self._user_input.update(user_input)

        try:
            self._user_input[CONF_TOKEN] = await self._login()

            if self._reauth_entry:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=self._user_input
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)

                return self.async_abort(reason="reauth_successful")

            return self.async_create_entry(title=NAME, data=self._user_input)
        except CannotConnect:
            self._errors["base"] = ERROR_CANNOT_CONNECT
        except InvalidAuth:
            self._errors["base"] = ERROR_INVALID_AUTH
        except Exception as error:  # pylint: disable=broad-exception-caught
            _LOGGER.exception(error)
            self._errors["base"] = ERROR_UNKNOWN

        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SuperSocoCustomOptionsFlowHandler(config_entry)

    async def _login(self):
        try:
            if self._user_input[CONF_APP_NAME] == SUPER_SOCO:
                client = self._get_super_soco_client()
                await client.login()
            else:
                client = self._get_vmoto_soco_client()
                await client.login(self._user_input[CONF_LOGIN_CODE])

            token = await client.get_token()

            return token
        except ServerTimeoutError as exc:
            raise CannotConnect from exc
        except ClientResponseError as error:
            if error.status == 400:
                raise InvalidAuth from error

            _LOGGER.error(error)

            raise error

    async def _get_login_code(self) -> bool:
        try:
            client = self._get_vmoto_soco_client()

            await client.get_login_code()

            return True
        except ServerTimeoutError as exc:
            raise CannotConnect from exc
        except ClientResponseError as error:
            if error.status == 400:
                raise InvalidAuth from error

            _LOGGER.error(error)

            raise error

    def _get_session(self) -> ClientSession:
        if not self._session:
            self._session = async_create_clientsession(self.hass)

        return self._session

    def _get_super_soco_client(self) -> SuperSocoAPI:
        return SuperSocoAPI(
            self._get_session(),
            self._user_input[CONF_PHONE_PREFIX],
            self._user_input[CONF_PHONE_NUMBER],
            self._user_input[CONF_PASSWORD],
        )

    def _get_vmoto_soco_client(self) -> VmotoSocoAPI:
        return VmotoSocoAPI(
            self._get_session(),
            self._user_input[CONF_PHONE_PREFIX],
            self._user_input[CONF_PHONE_NUMBER],
        )


class SuperSocoCustomOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input=None  # pylint: disable=unused-argument
    ) -> FlowResult:
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
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

    async def _update_options(self) -> FlowResult:
        return self.async_create_entry(title=NAME, data=self.options)
