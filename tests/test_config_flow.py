"""Test vmoto config flow."""

from typing import cast
from unittest.mock import AsyncMock, create_autospec, patch

import pytest
from aiohttp import (
    ClientResponseError,
    ClientSession,
    ServerTimeoutError,
)
from aiohttp.client_reqrep import RequestInfo
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from multidict import (
    CIMultiDict,
    CIMultiDictProxy,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry
from yarl import URL

from custom_components.super_soco_custom.config_flow import (
    ConfigFlow,
    VmotoOptionsFlowHandler,
)
from custom_components.super_soco_custom.const import (
    CONF_LOGIN_CODE,
    CONF_LOGIN_METHOD,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    DOMAIN,
    LOGIN_METHOD_EMAIL,
    LOGIN_METHOD_PHONE,
    NAME,
    OPT_EMAIL,
    OPT_ENABLE_ALTITUDE_ENTITY,
    OPT_ENABLE_LAST_TRIP_ENTITIES,
    OPT_ENABLE_LAST_WARNING_ENTITY,
    OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
    OPT_UPDATE_INTERVAL,
)
from custom_components.super_soco_custom.errors import (
    CannotConnect,
    InvalidAuth,
)
from custom_components.super_soco_custom.vmoto_api import VmotoAPI

from .const import MOCK_VMOTO_CONFIG


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with (
        patch(
            "custom_components.super_soco_custom.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.super_soco_custom.async_setup_entry",
            return_value=True,
        ),
    ):
        yield


# Here we simulate a successful config flow from the backend.
# Note that we use the `bypass_vmoto_get_login_code` and
# `bypass_vmoto_login` fixtures here because we want the config flow
# validation to succeed during the test.
@pytest.mark.asyncio
async def test_successful_vmoto_config_flow(
    hass,
    bypass_vmoto_get_login_code,
    bypass_vmoto_login,
):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the login method form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Continue past the login method step (select phone)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_LOGIN_METHOD: LOGIN_METHOD_PHONE},
    )

    # Check that the config flow shows the credentials form as the next step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "credentials"

    # Continue past the credentials step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_PHONE_PREFIX: MOCK_VMOTO_CONFIG[CONF_PHONE_PREFIX],
            CONF_PHONE_NUMBER: MOCK_VMOTO_CONFIG[CONF_PHONE_NUMBER],
        },
    )

    # Check that the config flow shows the login code form as the next step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "login_code"

    # Continue past the login code step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_LOGIN_CODE: MOCK_VMOTO_CONFIG[CONF_LOGIN_CODE]},
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME
    assert result["result"]


# Our config flow also has an options flow, so we must test it as well.
@pytest.mark.asyncio
async def test_options_flow(hass):
    """Test an options flow."""
    # Create a new MockConfigEntry and add to HASS (we're bypassing config
    # flow entirely)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG, entry_id="test")
    entry.add_to_hass(hass)

    # Initialize an options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    # Verify that the first options step is a user form
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Enter some fake data into the form
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            OPT_UPDATE_INTERVAL: 5,
        },
    )

    # Verify that the flow finishes
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == NAME

    # Verify that the options were updated
    assert entry.options == {
        OPT_UPDATE_INTERVAL: 5,
        OPT_EMAIL: "",
        OPT_ENABLE_ALTITUDE_ENTITY: True,
        OPT_ENABLE_LAST_TRIP_ENTITIES: True,
        OPT_ENABLE_LAST_WARNING_ENTITY: True,
        OPT_ENABLE_REVERSE_GEOCODING_ENTITY: False,
    }


@pytest.mark.asyncio
async def test_async_step_reauth_and_get_session(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_VMOTO_CONFIG)
    entry.add_to_hass(hass)

    flow = ConfigFlow()
    flow.hass = hass
    # simulate flow context with entry_id
    flow.context = {"entry_id": entry.entry_id}

    # call reauth step which delegates to async_step_user
    res = await flow.async_step_reauth()
    assert isinstance(res, dict)
    assert res.get("type") in ("form", "create_entry", "abort")

    # test _get_session caching
    s1 = flow._get_session()
    s2 = flow._get_session()
    assert isinstance(s1, ClientSession)
    assert s1 is s2


@pytest.mark.asyncio
async def test_async_step_reauth_with_no_entry_id(hass):
    """Ensure async_step_reauth handles missing context['entry_id'] gracefully."""
    flow = ConfigFlow()
    flow.hass = hass
    # no entry_id in context
    flow.context = {}

    res = await flow.async_step_reauth()
    assert isinstance(res, dict)
    assert res.get("type") in ("form", "create_entry", "abort")


@pytest.mark.asyncio
async def test_async_step_login_cannot_connect(hass, monkeypatch):
    flow = ConfigFlow()
    flow.hass = hass

    monkeypatch.setattr(flow, "_login", lambda: (_ for _ in ()).throw(CannotConnect()))
    res = await flow.async_step_login()
    assert isinstance(res, dict)
    assert res.get("type") == "form"
    assert (res.get("errors") or {}).get("base") == "cannot_connect"


@pytest.mark.asyncio
async def test_async_step_login_code_cannot_connect(hass, monkeypatch):
    """async_step_login_code sets ERROR_CANNOT_CONNECT when _get_login_code raises CannotConnect."""
    flow = ConfigFlow()
    flow.hass = hass
    flow._user_input[CONF_LOGIN_METHOD] = LOGIN_METHOD_PHONE

    monkeypatch.setattr(
        flow,
        "_get_login_code",
        lambda: (_ for _ in ()).throw(CannotConnect()),
    )

    res = await flow.async_step_login_code()
    assert res.get("type") == "form"
    assert res.get("errors", {}).get("base") == "cannot_connect"


@pytest.mark.asyncio
async def test_config_flow_error_branches(
    hass, monkeypatch, make_client_response_error
):
    flow = ConfigFlow()
    flow.hass = hass

    BadClientErr = make_client_response_error(status=500)

    bad_vm_client = create_autospec(VmotoAPI, instance=True)
    bad_vm_client.get_login_code = AsyncMock(side_effect=BadClientErr)
    monkeypatch.setattr(flow, "_get_vmoto_client", lambda: bad_vm_client)

    with pytest.raises(ClientResponseError):
        await flow._get_login_code()


@pytest.mark.asyncio
async def test_get_session_and_clients(hass):
    """The ConfigFlow should memoize the session and create clients."""
    flow = ConfigFlow()
    flow.hass = hass

    sess1 = flow._get_session()
    sess2 = flow._get_session()

    assert sess1 is sess2

    flow._user_input.update(MOCK_VMOTO_CONFIG)
    vmoto_client = flow._get_vmoto_client()

    assert isinstance(vmoto_client, VmotoAPI)


def test_async_get_options_flow_returns_handler():
    """async_get_options_flow should return the options flow handler."""
    entry = MockConfigEntry(domain=DOMAIN, data={}, entry_id="test")

    handler = ConfigFlow.async_get_options_flow(entry)

    assert isinstance(handler, VmotoOptionsFlowHandler)


@pytest.mark.asyncio
async def test_get_login_code_success(hass):
    flow = ConfigFlow()
    flow.hass = hass

    good_client = create_autospec(VmotoAPI, instance=True)
    good_client.get_login_code = AsyncMock(return_value={"ok": True})
    flow._get_vmoto_client = lambda: good_client
    assert await flow._get_login_code() is True


@pytest.mark.asyncio
async def test_get_login_code_raises_invalid_auth_on_400(hass):
    flow = ConfigFlow()
    flow.hass = hass

    req_info = RequestInfo(
        URL("http://localhost"),
        "GET",
        cast("CIMultiDictProxy[str]", CIMultiDict()),
        URL("http://localhost"),
    )
    bad_client = create_autospec(VmotoAPI, instance=True)
    bad_client.get_login_code = AsyncMock(
        side_effect=ClientResponseError(req_info, (), status=400, message="bad")
    )
    flow._get_vmoto_client = lambda: bad_client
    with pytest.raises(InvalidAuth):
        await flow._get_login_code()


@pytest.mark.asyncio
async def test_get_login_code_raises_cannot_connect_on_timeout(hass):
    flow = ConfigFlow()
    flow.hass = hass

    timeout_client = create_autospec(VmotoAPI, instance=True)
    timeout_client.get_login_code = AsyncMock(side_effect=ServerTimeoutError())
    flow._get_vmoto_client = lambda: timeout_client
    with pytest.raises(CannotConnect):
        await flow._get_login_code()


@pytest.mark.asyncio
async def test_async_step_app_handles_get_login_code_errors(hass, monkeypatch):
    """async_step_credentials should return form with errors when _get_login_code fails."""
    flow = ConfigFlow()
    flow.hass = hass
    flow._user_input[CONF_LOGIN_METHOD] = LOGIN_METHOD_PHONE

    monkeypatch.setattr(
        flow,
        "_get_login_code",
        lambda: (_ for _ in ()).throw(InvalidAuth()),
    )

    res = await flow.async_step_credentials(
        {
            CONF_PHONE_NUMBER: "123",
            CONF_PHONE_PREFIX: 1,
        }
    )

    assert res.get("type") == "form"
    assert res.get("errors") == {"base": "invalid_auth"}


@pytest.mark.asyncio
async def test_async_step_login_reauth_success(hass, monkeypatch):
    """async_step_login should handle reauth by updating entry and aborting."""
    flow = ConfigFlow()
    flow.hass = hass

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    flow.context = {"entry_id": entry.entry_id}

    async def fake_login(self=None):
        return "token"

    monkeypatch.setattr(ConfigFlow, "_login", fake_login)

    res = await flow.async_step_login()

    assert isinstance(res, dict)
    assert res.get("type") == "abort"
    assert res.get("reason") == "reauth_successful"


@pytest.mark.asyncio
async def test_async_step_app_handles_unknown_exception(hass, monkeypatch):
    """If _get_login_code raises a generic exception, flow should set ERROR_UNKNOWN."""
    flow = ConfigFlow()
    flow.hass = hass
    flow._user_input[CONF_LOGIN_METHOD] = LOGIN_METHOD_PHONE

    monkeypatch.setattr(
        flow,
        "_get_login_code",
        lambda: (_ for _ in ()).throw(Exception("boom")),
    )

    result2 = await flow.async_step_credentials(
        {
            CONF_PHONE_NUMBER: "123",
            CONF_PHONE_PREFIX: 1,
        }
    )

    assert result2.get("type") == "form"
    assert (result2.get("errors") or {}).get("base") == "unknown"


@pytest.mark.asyncio
async def test_async_step_login_handles_unknown_on_login_exception(hass, monkeypatch):
    """If _login raises an unexpected exception, async_step_login should set ERROR_UNKNOWN."""
    flow = ConfigFlow()
    flow.hass = hass

    async def bad_login(self=None):
        raise Exception("boom")

    monkeypatch.setattr(ConfigFlow, "_login", bad_login)

    res = await flow.async_step_login()
    assert isinstance(res, dict)
    assert res.get("type") == "form"
    errors = res.get("errors") or {}
    assert errors.get("base") == "unknown"


@pytest.mark.asyncio
async def test_async_step_user_already_configured(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # When an entry exists, calling async_step_user still shows the form
    flow = ConfigFlow()
    flow.hass = hass

    res = await flow.async_step_user({})

    assert isinstance(res, dict)
    assert res.get("type") == "form"


@pytest.mark.asyncio
async def test_async_step_login_handles_invalid_auth(hass, monkeypatch):
    flow = ConfigFlow()
    flow.hass = hass

    async def bad_login(self=None):
        raise InvalidAuth()

    monkeypatch.setattr(ConfigFlow, "_login", bad_login)

    res = await flow.async_step_login()

    assert isinstance(res, dict)
    assert res.get("type") == "form"
    errors = res.get("errors") or {}
    assert errors.get("base") == "invalid_auth"


@pytest.mark.asyncio
async def test_login_raises_invalid_auth_on_400(hass):
    flow = ConfigFlow()
    flow.hass = hass

    req_info = RequestInfo(
        URL("http://localhost"),
        "GET",
        cast("CIMultiDictProxy[str]", CIMultiDict()),
        URL("http://localhost"),
    )
    bad_client = create_autospec(VmotoAPI, instance=True)
    bad_client.login = AsyncMock(
        side_effect=ClientResponseError(req_info, (), status=400, message="bad")
    )
    bad_client.get_token = AsyncMock(return_value=None)
    flow._get_vmoto_client = lambda: bad_client
    with pytest.raises(InvalidAuth):
        await flow._login()


@pytest.mark.asyncio
async def test_login_raises_cannot_connect_on_timeout(hass):
    flow = ConfigFlow()
    flow.hass = hass

    timeout_client = create_autospec(VmotoAPI, instance=True)
    timeout_client.login = AsyncMock(side_effect=ServerTimeoutError())
    flow._get_vmoto_client = lambda: timeout_client
    with pytest.raises(CannotConnect):
        await flow._login()


@pytest.mark.asyncio
async def test_async_step_login_method_email_path(hass):
    """async_step_login_method shows email credentials form for email login method."""
    flow = ConfigFlow()
    flow.hass = hass
    flow._user_input[CONF_LOGIN_METHOD] = LOGIN_METHOD_EMAIL

    res = await flow.async_step_user({CONF_LOGIN_METHOD: LOGIN_METHOD_EMAIL})

    assert res.get("type") == "form"
    assert res.get("step_id") == "credentials"
    data_schema = res.get("data_schema")
    assert data_schema is not None
    schema_keys = [str(k) for k in data_schema.schema.keys()]
    assert any("email" in k.lower() for k in schema_keys)


@pytest.mark.asyncio
async def test_login_non_400_client_response_error_reraises(
    hass, make_client_response_error
):
    """_login re-raises non-400 ClientResponseError after logging it."""
    flow = ConfigFlow()
    flow.hass = hass

    err_500 = make_client_response_error(status=500)
    bad_client = create_autospec(VmotoAPI, instance=True)
    bad_client.login = AsyncMock(side_effect=err_500)
    flow._get_vmoto_client = lambda: bad_client

    with pytest.raises(ClientResponseError) as exc_info:
        await flow._login()

    assert exc_info.value.status == 500
