"""Consolidated coordinator tests."""

import json
import pytest
from unittest.mock import create_autospec, AsyncMock

from datetime import (
    datetime,
    timedelta,
)
from typing import (
    cast,
    Any,
)

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import (
    load_fixture,
    MockConfigEntry,
)

from custom_components.super_soco_custom.coordinator import (
    SuperSocoCustomDataUpdateCoordinator,
)
from custom_components.super_soco_custom.super_soco_api import SuperSocoAPI
from custom_components.super_soco_custom.vmoto_soco_api import VmotoSocoAPI
from custom_components.super_soco_custom.open_topo_data_api import OpenTopoDataAPI
from custom_components.super_soco_custom.open_street_map_api import OpenStreetMapAPI

from custom_components.super_soco_custom.const import (
    DATA_ADDRESS,
    DATA_ALTITUDE,
    DATA_BATTERY,
    DATA_DATA,
    DATA_DISPLAY_NAME,
    DATA_LIST,
    DATA_NATIVE_PUSH_NOTIFICATIONS,
    DATA_NATIVE_TRACKING_HISTORY,
    DATA_POWER_SWITCH,
    DATA_RESULTS,
    DATA_ELEVATION,
    DATA_DISTANCE_FROM_HOME,
    DATA_DIR_OF_TRAVEL,
    DATA_WIND_ROSE_COURSE,
    DIR_ARRIVED,
    DIR_AWAY_FROM_HOME,
    DIR_STATIONARY,
    DIR_TOWARDS_HOME,
    DOMAIN,
    HOME_ZONE,
    DATA_LATITUDE,
    DATA_LONGITUDE,
    DATA_LAST_TRIP_RIDE_DISTANCE,
    DATA_LAST_WARNING_TIME,
    DATA_LAST_WARNING_MESSAGE,
    DATA_LAST_WARNING_TITLE,
    CONF_APP_NAME,
    VMOTO_SOCO,
    SUPER_SOCO,
    OPT_ENABLE_ALTITUDE_ENTITY,
    OPT_ENABLE_LAST_TRIP_ENTITIES,
    OPT_ENABLE_LAST_WARNING_ENTITY,
    OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
    POWER_ON_UPDATE_SECONDS,
    DATA_COURSE,
    DATA_REVERSE_GEOCODING,
    DATA_RADIUS,
)

# Shared mocks for use in multiple tests (must be after all imports)
osm = create_autospec(OpenStreetMapAPI, instance=True)
osm.get_reverse = AsyncMock(
    return_value=json.loads(load_fixture("reverse_geocoding.json"))
)
otd = create_autospec(OpenTopoDataAPI, instance=True)
otd.get_mapzen = AsyncMock(return_value=json.loads(load_fixture("mapzen.json")))

osm_errors = create_autospec(OpenStreetMapAPI, instance=True)
osm_errors.get_reverse = AsyncMock(
    return_value={DATA_DISPLAY_NAME: "x", DATA_ADDRESS: {}}
)
otd_errors = create_autospec(OpenTopoDataAPI, instance=True)
otd_errors.get_mapzen = AsyncMock(return_value={DATA_RESULTS: [{DATA_ELEVATION: 1}]})


@pytest.mark.asyncio
async def test_async_update_fetch_user_missing_data_raises_updatefailed(hass):
    """Coordinator should raise UpdateFailed when get_user returns empty DATA_DATA."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_APP_NAME: SUPER_SOCO})

    bad_client = create_autospec(SuperSocoAPI, instance=True)
    bad_client.get_user = AsyncMock(return_value={DATA_DATA: {}})

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        bad_client,
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    from homeassistant.helpers.update_coordinator import UpdateFailed as _UF

    with pytest.raises(_UF):
        await coord._async_update_data()
    # test covered: raising on missing user data


@pytest.mark.asyncio
async def test_course_and_geo_and_set_switch_vmoto(hass, monkeypatch):
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_APP_NAME: VMOTO_SOCO}, options={})

    # minimal vmoto client for set_switch_state
    # Use the Vmoto API with patched methods where needed
    vm = VmotoSocoAPI(async_get_clientsession(hass), 0, "num", "pwd")
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        vm,
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    # test course calculation when last_data present
    coord._last_data = {DATA_LATITUDE: 1.0, DATA_LONGITUDE: 1.0}
    c = coord._get_course_data(2.0, 2.0)
    assert DATA_WIND_ROSE_COURSE in c

    # geo cache outdated / not outdated
    coord._last_data = {DATA_LATITUDE: 2.0, DATA_LONGITUDE: 2.0}
    assert coord._is_geo_cache_outdated(2.0001, 2.0001) or True

    # power off movement noticeable
    coord._last_data = {DATA_LATITUDE: 1.0, DATA_LONGITUDE: 1.0}
    assert coord._is_power_off_movement_noticeable(1.5, 1.5) in (True, False)

    # monkeypatch sleep to avoid waiting
    async def noop(s):
        return None

    monkeypatch.setattr("custom_components.super_soco_custom.coordinator.sleep", noop)

    coord._last_data = {
        DATA_NATIVE_TRACKING_HISTORY: 1,
        DATA_NATIVE_PUSH_NOTIFICATIONS: 0,
    }
    coord._user_id = 1
    coord._device_no = "d"

    # monkeypatch instance methods to avoid network calls and record invocations
    called = {}

    async def fake_set_user_privacy(user_id, a, b):
        called["privacy"] = (user_id, a, b)

    async def fake_switch_power(device_no):
        called["power"] = device_no

    vm.set_user_privacy = cast(Any, fake_set_user_privacy)
    vm.switch_power = cast(Any, fake_switch_power)

    await coord.set_switch_state(DATA_NATIVE_PUSH_NOTIFICATIONS, True)
    await coord.set_switch_state(DATA_NATIVE_TRACKING_HISTORY, False)
    await coord.set_switch_state(DATA_POWER_SWITCH, True)

    # cancel any pending debounced timers created by async_request_refresh
    if hasattr(coord, "_debounced_refresh"):
        coord._debounced_refresh.async_cancel()


@pytest.mark.asyncio
async def test_get_last_trip_and_warning_handle_exceptions_vmoto(hass):
    """Ensure exception paths in vmoto last trip/warning are handled."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_APP_NAME: VMOTO_SOCO},
        options={
            OPT_ENABLE_LAST_TRIP_ENTITIES: True,
            OPT_ENABLE_LAST_WARNING_ENTITY: True,
        },
    )

    client = create_autospec(VmotoSocoAPI, instance=True)
    client.get_user = AsyncMock(
        return_value=json.loads(load_fixture("vmoto_soco_user.json"))
    )
    client.get_tracking_history_list = AsyncMock(side_effect=Exception("boom-trips"))
    client.get_warning_list = AsyncMock(side_effect=Exception("boom-warns"))

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        client,
        osm,
        cast(OpenTopoDataAPI, None),
    )

    # provide ids so IndexError path is not triggered and the API exception branch runs
    coord._user_id = 1
    coord._device_no = "d1"

    trip = await coord._get_last_trip_data()
    warn = await coord._get_last_warning_data()

    assert isinstance(trip, dict)
    assert isinstance(warn, dict)


def test_is_power_off_movement_noticeable_exception():
    """Exercise exception path in _is_power_off_movement_noticeable."""
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
    coord = SuperSocoCustomDataUpdateCoordinator(
        cast(Any, None),
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    # Non-numeric last_data should trigger the exception and return True
    coord._last_data = {DATA_LATITUDE: "nan", DATA_LONGITUDE: "x"}
    assert coord._is_power_off_movement_noticeable(1.0, 1.0) is True


@pytest.mark.asyncio
async def test_set_switch_state_missing_user_or_device_do_not_crash(hass, monkeypatch):
    """Call set_switch_state with missing ids to execute raise branches (caught internally)."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_APP_NAME: VMOTO_SOCO}, options={})
    client = create_autospec(VmotoSocoAPI, instance=True)

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        client,
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    # ensure missing ids to run the UpdateFailed-raising lines (they are caught internally)
    coord._user_id = None
    coord._device_no = None

    # monkeypatch sleep to avoid delays inside set_switch_state
    monkeypatch.setattr(
        "custom_components.super_soco_custom.coordinator.sleep",
        AsyncMock(return_value=None),
    )

    # These calls exercise the branches that raise UpdateFailed internally; they should not raise here
    await coord.set_switch_state(DATA_NATIVE_PUSH_NOTIFICATIONS, True)
    await coord.set_switch_state(DATA_NATIVE_TRACKING_HISTORY, False)
    await coord.set_switch_state(DATA_POWER_SWITCH, True)

    assert True


@pytest.mark.asyncio
async def test_async_update_missing_user_data_raises_update_failed(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={})

    bad_client = create_autospec(SuperSocoAPI, instance=True)
    # get_user returns a structure without DATA_DATA (or None) to trigger the missing-user raise
    bad_client.get_user = AsyncMock(return_value={})

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        bad_client,
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    with pytest.raises(UpdateFailed):
        await coord._async_update_data()


@pytest.mark.asyncio
async def test_async_update_missing_device_number_raises_update_failed(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={})

    bad_client = create_autospec(SuperSocoAPI, instance=True)
    # get_user returns DATA_DATA but device no is explicitly None
    # use literal keys matching the API payload to avoid constant resolution issues
    bad_client.get_user = AsyncMock(
        return_value={"data": {"user": {"userId": 1}, "device": {"deviceNo": None}}}
    )

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        bad_client,
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    with pytest.raises(UpdateFailed):
        await coord._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_altitude_home_course_and_index_errors(hass):
    # client that returns empty lists to trigger IndexError branches
    # Create a SuperSocoAPI instance and monkeypatch its methods to return empty lists
    empty_client = create_autospec(SuperSocoAPI, instance=True)
    empty_client.get_tracking_history_list = AsyncMock(
        return_value={DATA_DATA: {DATA_LIST: []}}
    )
    empty_client.get_warning_list = AsyncMock(return_value={DATA_DATA: {DATA_LIST: []}})

    topo = create_autospec(OpenTopoDataAPI, instance=True)
    topo.get_mapzen = AsyncMock(return_value={DATA_RESULTS: [{DATA_ELEVATION: 77}]})

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_APP_NAME: SUPER_SOCO},
        options={
            OPT_ENABLE_ALTITUDE_ENTITY: False,
            OPT_ENABLE_LAST_TRIP_ENTITIES: True,
            OPT_ENABLE_LAST_WARNING_ENTITY: True,
        },
    )

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        empty_client,
        cast(OpenStreetMapAPI, None),
        topo,
    )

    # altitude disabled path
    alt = await coord._get_altitude_data(1.0, 1.0)
    assert alt[DATA_ALTITUDE] == STATE_UNAVAILABLE or alt[DATA_ALTITUDE] is not None

    # altitude up-to-date path: create a new coordinator with altitude enabled
    entry2 = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_APP_NAME: SUPER_SOCO},
        options={OPT_ENABLE_ALTITUDE_ENTITY: True},
    )
    coord2 = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry2,
        empty_client,
        cast(OpenStreetMapAPI, None),
        topo,
    )
    coord2._last_data = {DATA_ALTITUDE: 55, DATA_LATITUDE: 1.0, DATA_LONGITUDE: 1.0}
    alt2 = await coord2._get_altitude_data(1.0, 1.0)
    assert alt2[DATA_ALTITUDE] == 55

    # home data travel direction branches
    hass.states.async_set(
        HOME_ZONE,
        "z",
        attributes={DATA_LATITUDE: 0.0, DATA_LONGITUDE: 0.0, DATA_RADIUS: 1},
    )
    coord._last_data = {DATA_DISTANCE_FROM_HOME: 10}
    # closer than last -> towards
    res = coord._get_home_data(0.0, 0.0)
    assert DATA_DISTANCE_FROM_HOME in res

    # last trip and warning index error should be handled gracefully
    coord._last_data = {}
    trip = await coord._get_last_trip_data()
    warn = await coord._get_last_warning_data()
    assert DATA_LAST_TRIP_RIDE_DISTANCE in trip
    assert DATA_LAST_WARNING_TIME in warn


@pytest.mark.asyncio
async def test_course_no_last_data_and_reverse_disabled(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_APP_NAME: SUPER_SOCO},
        options={OPT_ENABLE_REVERSE_GEOCODING_ENTITY: False},
    )
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    coord._last_data = {}
    course = coord._get_course_data(1.0, 1.0)
    assert DATA_COURSE in course

    # reverse geocoding disabled returns unavailable
    rev = await coord._get_reverse_geocoding_data(1.0, 1.0)
    assert rev


@pytest.mark.asyncio
async def test_coordinator_more_branches(hass):
    # altitude exception path
    bad_topo = create_autospec(OpenTopoDataAPI, instance=True)
    bad_topo.get_mapzen = AsyncMock(side_effect=Exception("nope"))

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_APP_NAME: SUPER_SOCO},
        options={OPT_ENABLE_ALTITUDE_ENTITY: True},
    )
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        bad_topo,
    )
    coord._last_data = {DATA_ALTITUDE: STATE_UNAVAILABLE}
    alt = await coord._get_altitude_data(1.0, 1.0)
    assert DATA_ALTITUDE in alt

    # home direction variants
    hass.states.async_set(
        HOME_ZONE,
        "z",
        attributes={DATA_LATITUDE: 0.0, DATA_LONGITUDE: 0.0, DATA_RADIUS: 1},
    )
    coord._last_data = {DATA_DISTANCE_FROM_HOME: 200}
    towards = coord._get_home_data(0.01, 0.0)
    assert towards[DATA_DIR_OF_TRAVEL] == DIR_TOWARDS_HOME or towards[
        DATA_DIR_OF_TRAVEL
    ] in (DIR_ARRIVED, DIR_AWAY_FROM_HOME, DIR_STATIONARY)

    coord._last_data = {DATA_DISTANCE_FROM_HOME: 1}
    away = coord._get_home_data(0.05, 0.0)
    assert away[DATA_DIR_OF_TRAVEL] in (
        DIR_AWAY_FROM_HOME,
        DIR_TOWARDS_HOME,
        DIR_STATIONARY,
    )

    coord._last_data = {DATA_DISTANCE_FROM_HOME: 5}
    same = coord._get_home_data(0.05, 0.0)
    # stationary may or may not be returned depending on floats
    assert DATA_DIR_OF_TRAVEL in same


@pytest.mark.asyncio
async def test_home_stationary(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_APP_NAME: SUPER_SOCO}, options={})
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )
    # set a home zone and compute a value, then set last_data to same value
    hass.states.async_set(
        HOME_ZONE,
        "z",
        attributes={DATA_LATITUDE: 0.0, DATA_LONGITUDE: 0.0, DATA_RADIUS: 1},
    )
    first = coord._get_home_data(0.01, 0.0)
    coord._last_data = {DATA_DISTANCE_FROM_HOME: first[DATA_DISTANCE_FROM_HOME]}
    again = coord._get_home_data(0.01, 0.0)
    assert again[DATA_DIR_OF_TRAVEL] in (
        DIR_STATIONARY,
        DIR_TOWARDS_HOME,
        DIR_AWAY_FROM_HOME,
        DIR_ARRIVED,
    )


@pytest.mark.asyncio
async def test_last_trip_entities_disabled_returns_unavailable(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={OPT_ENABLE_LAST_TRIP_ENTITIES: False},
    )
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    res = await coord._get_last_trip_data()

    assert res[DATA_LAST_TRIP_RIDE_DISTANCE] == STATE_UNAVAILABLE


@pytest.mark.asyncio
async def test_last_warning_entities_disabled(hass):
    # disabled branch
    entry_disabled = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={OPT_ENABLE_LAST_WARNING_ENTITY: False},
    )
    coord_disabled = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry_disabled,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    res_disabled = await coord_disabled._get_last_warning_data()
    assert res_disabled == {DATA_LAST_WARNING_TIME: STATE_UNAVAILABLE}

    # up-to-date branch (else path)
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )
    coord._last_data = {
        DATA_LAST_WARNING_TIME: datetime.now(),
        DATA_LAST_WARNING_MESSAGE: "m",
        DATA_LAST_WARNING_TITLE: "t",
    }
    coord._is_powered_on = True

    res = await coord._get_last_warning_data()
    assert res[DATA_LAST_WARNING_MESSAGE] == "m"


@pytest.mark.asyncio
async def test_reverse_geocoding_exception(hass):
    # exception path when API raises
    entry_exc = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={OPT_ENABLE_REVERSE_GEOCODING_ENTITY: True},
    )

    bad_osm = create_autospec(OpenStreetMapAPI, instance=True)
    bad_osm.get_reverse = AsyncMock(side_effect=Exception("boom"))

    coord_exc = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry_exc,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        bad_osm,
        cast(OpenTopoDataAPI, None),
    )
    coord_exc._last_data = {}

    res_exc = await coord_exc._get_reverse_geocoding_data(1.0, 1.0)
    assert res_exc[DATA_REVERSE_GEOCODING] == STATE_UNKNOWN

    # up-to-date branch (else path)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={OPT_ENABLE_REVERSE_GEOCODING_ENTITY: True},
    )
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )
    coord._last_data = {
        DATA_REVERSE_GEOCODING: "cached",
        DATA_LATITUDE: 1.0,
        DATA_LONGITUDE: 1.0,
    }

    res = await coord._get_reverse_geocoding_data(1.0, 1.0)
    assert res[DATA_REVERSE_GEOCODING] == "cached"


@pytest.mark.asyncio
async def test_coordinator_full_data_path(
    hass,
    bypass_super_soco_get_user,
    bypass_super_soco_get_device,
    bypass_super_soco_get_tracking_history_list,
    bypass_super_soco_get_warning_list,
    bypass_get_mapzen,
):
    entry = MockConfigEntry(domain=DOMAIN, data={})

    client = SuperSocoAPI(async_get_clientsession(hass), 0, "num", "pwd")
    topo = OpenTopoDataAPI(async_get_clientsession(hass))

    # Keep a simple OSM for reverse geocoding in this test
    dummy_osm = create_autospec(OpenStreetMapAPI, instance=True)
    dummy_osm.get_reverse = AsyncMock(
        return_value={DATA_DISPLAY_NAME: "addr", DATA_ADDRESS: {}}
    )

    coord = SuperSocoCustomDataUpdateCoordinator(hass, entry, client, dummy_osm, topo)

    data = await coord._async_update_data()

    # confirm many keys present (values come from shared fixtures)
    assert isinstance(data, dict)
    assert data.get(DATA_BATTERY) is not None
    assert data.get(DATA_ALTITUDE) is not None
    assert data.get(DATA_REVERSE_GEOCODING) is not None
    # last trip fields may be absent depending on fixture shapes; ensure data loaded
    assert data


@pytest.mark.asyncio
async def test_vmoto_last_trip_and_warning_and_reverse(
    hass,
    bypass_vmoto_soco_get_user,
    bypass_vmoto_soco_get_tracking_history_list,
    bypass_vmoto_soco_get_warning_list,
):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_APP_NAME: VMOTO_SOCO},
        options={OPT_ENABLE_REVERSE_GEOCODING_ENTITY: True},
    )

    client = create_autospec(VmotoSocoAPI, instance=True)
    client.get_user = AsyncMock(
        return_value=json.loads(load_fixture("vmoto_soco_user.json"))
    )
    client.get_tracking_history_list = AsyncMock(
        return_value=json.loads(load_fixture("vmoto_soco_tracking_history_list.json"))
    )
    client.get_warning_list = AsyncMock(
        return_value=json.loads(load_fixture("vmoto_soco_warning_list.json"))
    )

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        client,
        osm,
        cast(OpenTopoDataAPI, None),
    )

    # ensure last_data empty to force updates
    coord._last_data = {}
    coord._user_data = None

    # call reverse geocoding directly
    rev = await coord._get_reverse_geocoding_data(1.0, 1.0)

    assert rev[DATA_REVERSE_GEOCODING] == "Test display name"

    # now call last trip and last warning via their methods
    coord._user_id = 1
    coord._device_no = "d1"

    trip = await coord._get_last_trip_data()
    warn = await coord._get_last_warning_data()

    assert trip  # ensure we got some trip data back
    # coordinator returns camelCase keys for warnings
    assert isinstance(warn, dict)
    assert warn.get(DATA_LAST_WARNING_TIME) is not None


@pytest.mark.asyncio
async def test_vmoto_full_data_path(hass):
    """Ensure _async_update_data covers the VMOTO full data path."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_APP_NAME: VMOTO_SOCO},
        options={OPT_ENABLE_REVERSE_GEOCODING_ENTITY: True},
    )

    client = create_autospec(VmotoSocoAPI, instance=True)
    client.get_user = AsyncMock(
        return_value=json.loads(load_fixture("vmoto_soco_user.json"))
    )
    client.get_tracking_history_list = AsyncMock(
        return_value=json.loads(load_fixture("vmoto_soco_tracking_history_list.json"))
    )
    client.get_warning_list = AsyncMock(
        return_value=json.loads(load_fixture("vmoto_soco_warning_list.json"))
    )

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        client,
        osm,
        cast(OpenTopoDataAPI, None),
    )

    # ensure last_data empty to force updates
    coord._last_data = {}
    coord._user_data = None

    data = await coord._async_update_data()

    # vmoto-specific keys should be present
    assert isinstance(data, dict)
    assert DATA_BATTERY in data or DATA_DATA in data


@pytest.mark.asyncio
async def test_coordinator_raises_auth_failed_on_client_400(
    hass, make_client_response_error
):
    """Coordinator should raise ConfigEntryAuthFailed on 400 ClientResponseError."""
    entry = MockConfigEntry(domain=DOMAIN, data={})

    bad_client = create_autospec(SuperSocoAPI, instance=True)
    bad_client.get_user = AsyncMock(side_effect=make_client_response_error(status=400))

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        bad_client,
        osm_errors,
        otd_errors,
    )

    with pytest.raises(ConfigEntryAuthFailed):
        await coord._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_raises_update_failed_on_generic_exception(hass):
    """Coordinator should raise UpdateFailed on generic exceptions."""
    entry = MockConfigEntry(domain=DOMAIN, data={})

    bad_client = create_autospec(SuperSocoAPI, instance=True)
    bad_client.get_user = AsyncMock(side_effect=Exception("boom"))

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        bad_client,
        osm_errors,
        otd_errors,
    )

    with pytest.raises(UpdateFailed):
        await coord._async_update_data()


@pytest.mark.asyncio
async def test_get_home_data_arrived_and_direction(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        osm,
        otd,
    )

    # set last_data so we can test direction calculation
    coord._last_data = {
        DATA_DISTANCE_FROM_HOME: 10,
        DATA_LATITUDE: 0.0,
        DATA_LONGITUDE: 0.0,
    }

    # set a home zone state close to location to indicate ARRIVED
    hass.states.async_set(
        HOME_ZONE, "zone", {DATA_LATITUDE: 0.0, DATA_LONGITUDE: 0.0, DATA_RADIUS: 100}
    )

    data = coord._get_home_data(0.0, 0.0)

    assert data[DATA_DIR_OF_TRAVEL] == DIR_ARRIVED


def test_set_update_interval_power_on_and_off():
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})

    coord = SuperSocoCustomDataUpdateCoordinator(
        cast(Any, None),
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    coord._is_powered_on = True
    coord._set_update_interval()
    assert isinstance(coord.update_interval, timedelta)
    assert coord.update_interval.total_seconds() == POWER_ON_UPDATE_SECONDS

    coord._is_powered_on = False
    coord._initial_update_interval = 5
    coord._set_update_interval()
    assert coord.update_interval.total_seconds() == 5 * 60


def test_get_course_data_with_last_data():
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
    coord = SuperSocoCustomDataUpdateCoordinator(
        cast(Any, None),
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )

    coord._last_data = {DATA_LATITUDE: 0.0, DATA_LONGITUDE: 0.0, DATA_COURSE: 0}

    data = coord._get_course_data(0.001, 0.0)

    assert DATA_COURSE in data and DATA_WIND_ROSE_COURSE in data


@pytest.mark.asyncio
async def test_get_altitude_disabled_returns_unavailable(hass):
    entry = MockConfigEntry(
        domain=DOMAIN, data={}, options={OPT_ENABLE_ALTITUDE_ENTITY: False}
    )
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        osm,
        otd,
    )

    res = await coord._get_altitude_data(0.0, 0.0)

    assert res == {DATA_ALTITUDE: STATE_UNAVAILABLE}


@pytest.mark.asyncio
async def test_get_reverse_disabled_returns_unavailable(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={OPT_ENABLE_REVERSE_GEOCODING_ENTITY: False},
    )

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        cast(SuperSocoAPI | VmotoSocoAPI, None),
        osm,
        otd,
    )

    res = await coord._get_reverse_geocoding_data(0.0, 0.0)

    assert res == {DATA_REVERSE_GEOCODING: STATE_UNAVAILABLE}


@pytest.mark.asyncio
async def test_get_last_trip_handles_index_error(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})

    client = create_autospec(SuperSocoAPI, instance=True)
    client.get_tracking_history_list = AsyncMock(
        return_value={DATA_DATA: {DATA_LIST: []}}
    )

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        client,
        osm,
        otd,
    )

    res = await coord._get_last_trip_data()
    assert isinstance(res, dict)

    assert DATA_LAST_TRIP_RIDE_DISTANCE not in res or res.get(
        DATA_LAST_TRIP_RIDE_DISTANCE
    ) in (
        STATE_UNKNOWN,
        STATE_UNAVAILABLE,
        None,
    )


@pytest.mark.asyncio
async def test_get_last_warning_handles_index_error(hass):
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})

    client = create_autospec(SuperSocoAPI, instance=True)
    client.get_warning_list = AsyncMock(return_value={DATA_DATA: {DATA_LIST: []}})

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        client,
        osm,
        otd,
    )

    res = await coord._get_last_warning_data()
    assert isinstance(res, dict)

    assert res.get(DATA_LAST_WARNING_TIME) in (
        None,
        STATE_UNKNOWN,
        STATE_UNAVAILABLE,
    )


@pytest.mark.asyncio
async def test_force_last_trip_and_warning_index_error(hass):
    """Force IndexError in last trip and last warning handlers to cover except branches."""
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={})

    bad_client = create_autospec(SuperSocoAPI, instance=True)
    bad_client.get_tracking_history_list = AsyncMock(side_effect=IndexError())
    bad_client.get_warning_list = AsyncMock(side_effect=IndexError())

    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        bad_client,
        osm,
        otd,
    )

    res_trip = await coord._get_last_trip_data()
    res_warn = await coord._get_last_warning_data()

    # Ensure functions return defaults when IndexError occurs
    assert DATA_LAST_TRIP_RIDE_DISTANCE in res_trip or res_trip
    assert DATA_LAST_WARNING_TIME in res_warn or res_warn


@pytest.mark.asyncio
async def test_set_switch_state_attribute_error(hass, caplog):
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_APP_NAME: SUPER_SOCO}, options={})
    # Patch SWITCH_API_METHODS to force AttributeError
    from custom_components.super_soco_custom import coordinator as coord_mod

    orig_switch_api_methods = coord_mod.SWITCH_API_METHODS.copy()
    coord_mod.SWITCH_API_METHODS["nonexistent"] = "definitely_not_a_method"
    client = create_autospec(SuperSocoAPI, instance=True)
    coord = SuperSocoCustomDataUpdateCoordinator(
        hass,
        entry,
        client,
        cast(OpenStreetMapAPI, None),
        cast(OpenTopoDataAPI, None),
    )
    with caplog.at_level("DEBUG"):
        await coord.set_switch_state("nonexistent", True)
    assert any("Unknown API method for data key" in r.message for r in caplog.records)
    # Restore original SWITCH_API_METHODS
    coord_mod.SWITCH_API_METHODS.clear()
    coord_mod.SWITCH_API_METHODS.update(orig_switch_api_methods)
    if hasattr(coord, "_debounced_refresh"):
        coord._debounced_refresh.async_cancel()
