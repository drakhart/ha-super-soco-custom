import logging
from typing import cast

import voluptuous as vol
from aiohttp import ClientResponseError, ClientSession, ServerTimeoutError
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .const import (
    CONF_EMAIL,
    CONF_LOGIN_CODE,
    CONF_LOGIN_METHOD,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    CONF_TOKEN,
    CONFIG_FLOW_VERSION,
    DEFAULT_ENABLE_ALTITUDE_ENTITY,
    DEFAULT_ENABLE_LAST_TRIP_ENTITIES,
    DEFAULT_ENABLE_LAST_WARNING_ENTITY,
    DEFAULT_ENABLE_REVERSE_GEOCODING_ENTITY,
    DEFAULT_STRING,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
    ERROR_UNKNOWN,
    LOGIN_METHOD_EMAIL,
    LOGIN_METHOD_PHONE,
    MAX_UPDATE_INTERVAL_MINUTES,
    MIN_UPDATE_INTERVAL_MINUTES,
    NAME,
    OPT_EMAIL,
    OPT_ENABLE_ALTITUDE_ENTITY,
    OPT_ENABLE_LAST_TRIP_ENTITIES,
    OPT_ENABLE_LAST_WARNING_ENTITY,
    OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
    OPT_UPDATE_INTERVAL,
    PHONE_PREFIXES,
)
from .errors import CannotConnect, InvalidAuth
from .vmoto_api import VmotoAPI

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = CONFIG_FLOW_VERSION

    def __init__(self) -> None:
        self._errors = {}
        self._session = None
        self._reauth_entry = None
        self._user_input = {
            CONF_LOGIN_METHOD: None,
            CONF_PHONE_PREFIX: PHONE_PREFIXES[0][1],
            CONF_PHONE_NUMBER: None,
            CONF_EMAIL: None,
            CONF_LOGIN_CODE: None,
        }

    async def async_step_reauth(self, user_input=None) -> FlowResult:
        self._errors = {}
        entry_id: str | None = self.context.get("entry_id")
        if entry_id is None:
            self._reauth_entry = None
        else:
            self._reauth_entry = self.hass.config_entries.async_get_entry(entry_id)

        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input:
            self._user_input.update(user_input)

        errors = self._errors
        self._errors = {}

        return cast(
            "FlowResult",
            self.async_show_form(
                step_id="login_method",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_LOGIN_METHOD,
                            default=self._user_input[CONF_LOGIN_METHOD],
                        ): SelectSelector(
                            SelectSelectorConfig(
                                options=[LOGIN_METHOD_PHONE, LOGIN_METHOD_EMAIL],
                                translation_key=CONF_LOGIN_METHOD,
                            )
                        ),
                    }
                ),
                errors=errors,
            ),
        )

    async def async_step_login_method(self, user_input=None) -> FlowResult:
        if user_input:
            self._user_input.update(user_input)

        errors = self._errors
        self._errors = {}

        if self._user_input[CONF_LOGIN_METHOD] == LOGIN_METHOD_EMAIL:
            return cast(
                "FlowResult",
                self.async_show_form(
                    step_id="credentials",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                CONF_EMAIL, default=self._user_input[CONF_EMAIL]
                            ): str,
                        }
                    ),
                    errors=errors,
                ),
            )

        prefix_dict = {code: name for name, code in PHONE_PREFIXES}
        return cast(
            "FlowResult",
            self.async_show_form(
                step_id="credentials",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_PHONE_PREFIX,
                            default=self._user_input[CONF_PHONE_PREFIX],
                        ): vol.In(prefix_dict),
                        vol.Required(
                            CONF_PHONE_NUMBER,
                            default=self._user_input[CONF_PHONE_NUMBER],
                        ): str,
                    }
                ),
                errors=errors,
            ),
        )

    async def async_step_credentials(self, user_input=None) -> FlowResult:
        if user_input:
            self._user_input.update(user_input)

        try:
            await self._get_login_code()

            return cast(
                "FlowResult",
                self.async_show_form(
                    step_id="login_code",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_LOGIN_CODE): str,
                        }
                    ),
                    errors={},
                ),
            )
        except CannotConnect:
            self._errors["base"] = ERROR_CANNOT_CONNECT
        except InvalidAuth:
            self._errors["base"] = ERROR_INVALID_AUTH
        except Exception as error:
            _LOGGER.exception(error)
            self._errors["base"] = ERROR_UNKNOWN

        return await self.async_step_user(user_input)

    async def async_step_login_code(self, user_input=None) -> FlowResult:
        return await self.async_step_login(user_input)

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

                return cast("FlowResult", self.async_abort(reason="reauth_successful"))

            return cast(
                "FlowResult", self.async_create_entry(title=NAME, data=self._user_input)
            )
        except CannotConnect:
            self._errors["base"] = ERROR_CANNOT_CONNECT
        except InvalidAuth:
            self._errors["base"] = ERROR_INVALID_AUTH
        except Exception as error:
            _LOGGER.exception(error)
            self._errors["base"] = ERROR_UNKNOWN

        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VmotoOptionsFlowHandler(config_entry)

    async def _login(self):
        try:
            client = self._get_vmoto_client()
            await client.login(self._user_input[CONF_LOGIN_CODE])

            token = client.get_token()

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
            client = self._get_vmoto_client()

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

    def _get_vmoto_client(self) -> VmotoAPI:
        return VmotoAPI(
            self._get_session(),
            phone_prefix=self._user_input.get(CONF_PHONE_PREFIX),
            phone_number=self._user_input.get(CONF_PHONE_NUMBER),
            email=self._user_input.get(CONF_EMAIL),
        )


class VmotoOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None) -> FlowResult:
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            self.options.update(user_input)

            return await self._update_options()

        return cast(
            "FlowResult",
            self.async_show_form(
                step_id="user",
                description_placeholders={
                    "nominatim_url": "https://nominatim.org/release-docs/develop/api/Reverse/#other"
                },
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
                                OPT_ENABLE_ALTITUDE_ENTITY,
                                DEFAULT_ENABLE_ALTITUDE_ENTITY,
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
            ),
        )

    async def _update_options(self) -> FlowResult:
        return cast(
            "FlowResult", self.async_create_entry(title=NAME, data=self.options)
        )
