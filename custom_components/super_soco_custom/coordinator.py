import logging

from aiohttp import ClientResponseError
from asyncio import sleep
from datetime import datetime, timedelta

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ALARM_MODULE_MAX_VOLTAGE,
    API_GEO_PRECISION,
    CDN_BASE_URL,
    CONF_APP_NAME,
    DATA_ACCUMULATIVE_RIM,
    DATA_ADDRESS,
    DATA_AGREEMENT_END_TIME,
    DATA_AGREEMENT_START_TIME,
    DATA_ALARM_MODULE_BATTERY,
    DATA_ALARM_MODULE_VOLTAGE,
    DATA_ALTITUDE,
    DATA_BATTERY,
    DATA_CONTENT,
    DATA_COURSE,
    DATA_CREATE_TIME,
    DATA_DATA,
    DATA_DEVICE_NO,
    DATA_DEVICE,
    DATA_DIR_OF_TRAVEL,
    DATA_DISPLAY_NAME,
    DATA_DISTANCE_FROM_HOME,
    DATA_ELEVATION,
    DATA_ESTIMATED_RANGE,
    DATA_GPS_ACCURACY,
    DATA_LAST_GPS_TIME,
    DATA_LAST_TRIP_AVG_SPEED,
    DATA_LAST_TRIP_BEGIN_LATITUDE,
    DATA_LAST_TRIP_BEGIN_LONGITUDE,
    DATA_LAST_TRIP_BEGIN_TIME,
    DATA_LAST_TRIP_END_LATITUDE,
    DATA_LAST_TRIP_END_LONGITUDE,
    DATA_LAST_TRIP_END_TIME,
    DATA_LAST_TRIP_MILEAGE,
    DATA_LAST_TRIP_MINUTES,
    DATA_LAST_TRIP_RIDE_DISTANCE,
    DATA_LAST_TRIP_RIDE_TIME,
    DATA_LAST_WARNING_MESSAGE,
    DATA_LAST_WARNING_TIME,
    DATA_LAST_WARNING_TITLE,
    DATA_LATITUDE,
    DATA_LIST,
    DATA_LOCK,
    DATA_LOGO_IMAGE_URL,
    DATA_LONGITUDE,
    DATA_MODEL_NAME,
    DATA_NATIVE_PUSH_NOTIFICATIONS,
    DATA_NATIVE_TRACKING_HISTORY,
    DATA_POWER_STATUS,
    DATA_RADIUS,
    DATA_RESULTS,
    DATA_REVERSE_GEOCODING_CITY,
    DATA_REVERSE_GEOCODING_COUNTRY_CODE,
    DATA_REVERSE_GEOCODING_COUNTRY,
    DATA_REVERSE_GEOCODING_COUNTY,
    DATA_REVERSE_GEOCODING_HOUSE_NUMBER,
    DATA_REVERSE_GEOCODING_NEIGHBOURHOOD,
    DATA_REVERSE_GEOCODING_POSTCODE,
    DATA_REVERSE_GEOCODING_ROAD,
    DATA_REVERSE_GEOCODING_STATE_DISTRICT,
    DATA_REVERSE_GEOCODING_STATE,
    DATA_REVERSE_GEOCODING_VILLAGE,
    DATA_REVERSE_GEOCODING,
    DATA_SIGNAL_STRENGTH,
    DATA_SPEED,
    DATA_TITLE,
    DATA_TRIP_DISTANCE,
    DATA_USER_BIND_DEVICE,
    DATA_USER_ID,
    DATA_USER,
    DATA_VEHICLE_IMAGE_URL_VMOTO,
    DATA_VEHICLE_IMAGE_URL,
    DATA_WIND_ROSE_COURSE,
    DEFAULT_ENABLE_ALTITUDE_ENTITY,
    DEFAULT_ENABLE_LAST_TRIP_ENTITIES,
    DEFAULT_ENABLE_LAST_WARNING_ENTITY,
    DEFAULT_ENABLE_REVERSE_GEOCODING_ENTITY,
    DEFAULT_FLOAT,
    DEFAULT_INTEGER,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DIR_ARRIVED,
    DIR_AWAY_FROM_HOME,
    DIR_STATIONARY,
    DIR_TOWARDS_HOME,
    DISTANCE_ROUNDING_DECIMALS,
    DOMAIN,
    GPS_MAX_ACCURACY,
    HOME_ZONE,
    KM_IN_A_M,
    LAST_TRIP_CACHE_SECONDS,
    MINUTES_IN_AN_HOUR,
    OPT_ENABLE_ALTITUDE_ENTITY,
    OPT_ENABLE_LAST_TRIP_ENTITIES,
    OPT_ENABLE_LAST_WARNING_ENTITY,
    OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
    OPT_UPDATE_INTERVAL,
    POWER_OFF_DISTANCE_THRESHOLD_METERS,
    POWER_ON_UPDATE_SECONDS,
    SECONDS_IN_A_MINUTE,
    SIGNAL_MAX_STRENGTH,
    SWITCH_API_METHODS,
    SWITCH_REFRESH_SLEEP_SECONDS,
    VMOTO_SOCO,
)
from .helpers import (
    calculate_course,
    calculate_distance,
    calculate_percentage,
    calculate_wind_rose_course,
    parse_date,
    parse_timestamp,
)
from .open_street_map_api import OpenStreetMapAPI
from .open_topo_data_api import OpenTopoDataAPI
from .super_soco_api import SuperSocoAPI
from .vmoto_soco_api import VmotoSocoAPI

_LOGGER: logging.Logger = logging.getLogger(__package__)


class SuperSocoCustomDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: SuperSocoAPI | VmotoSocoAPI,
        open_street_map_api: OpenStreetMapAPI,
        open_topo_data_api: OpenTopoDataAPI,
    ) -> None:
        self._hass = hass
        self._config_entry = config_entry
        self._client = client
        self._open_street_map_api = open_street_map_api
        self._open_topo_data_api = open_topo_data_api
        self._last_data = {}
        self._initial_update_interval = int(
            config_entry.options.get(
                OPT_UPDATE_INTERVAL,
                DEFAULT_UPDATE_INTERVAL_MINUTES,
            )
        )
        self._is_powered_on = False
        self._last_trip_timestamp = None
        self._user_data = None
        self._user_id = None
        self._device_no = None

        _LOGGER.debug(
            "Setting initial update interval: %i minute(s)",
            self._initial_update_interval,
        )
        update_interval = timedelta(minutes=self._initial_update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        try:
            # Build main data
            if not self._user_data or self._is_app_vmoto_soco():
                _LOGGER.debug("Requesting user data")
                self._user_data = (await self._client.get_user())[DATA_DATA]

            self._user_id = self._user_data[DATA_USER][DATA_USER_ID]
            self._device_no = self._user_data[DATA_DEVICE][DATA_DEVICE_NO]

            if self._is_app_vmoto_soco():
                device_data = self._user_data[DATA_DEVICE]
            else:
                _LOGGER.debug("Requesting device data")
                device_data = (await self._client.get_device(self._device_no))[
                    DATA_DATA
                ]

            data = {
                DATA_ACCUMULATIVE_RIM: device_data[DATA_ACCUMULATIVE_RIM],
                DATA_ALARM_MODULE_BATTERY: calculate_percentage(
                    device_data[DATA_ALARM_MODULE_VOLTAGE] or DEFAULT_INTEGER,
                    ALARM_MODULE_MAX_VOLTAGE,
                ),
                DATA_ALARM_MODULE_VOLTAGE: device_data[DATA_ALARM_MODULE_VOLTAGE]
                or DEFAULT_INTEGER,
                DATA_BATTERY: device_data[DATA_BATTERY],
                DATA_TRIP_DISTANCE: round(
                    device_data[DATA_TRIP_DISTANCE], DISTANCE_ROUNDING_DECIMALS
                ),
                DATA_ESTIMATED_RANGE: device_data[DATA_ESTIMATED_RANGE],
                DATA_GPS_ACCURACY: calculate_percentage(
                    device_data[DATA_GPS_ACCURACY], GPS_MAX_ACCURACY
                ),
                DATA_LATITUDE: device_data[DATA_LATITUDE],
                DATA_LONGITUDE: device_data[DATA_LONGITUDE],
                DATA_NATIVE_PUSH_NOTIFICATIONS: device_data[
                    DATA_NATIVE_PUSH_NOTIFICATIONS
                ],
                DATA_NATIVE_TRACKING_HISTORY: device_data[DATA_NATIVE_TRACKING_HISTORY],
                DATA_POWER_STATUS: device_data[DATA_POWER_STATUS],
                DATA_SIGNAL_STRENGTH: calculate_percentage(
                    device_data[DATA_SIGNAL_STRENGTH], SIGNAL_MAX_STRENGTH
                ),
                DATA_SPEED: device_data[DATA_SPEED],
            }

            # Super Soco vs Vmoto Soco specific fields
            if self._is_app_vmoto_soco():
                data.update(
                    {
                        DATA_LAST_GPS_TIME: parse_timestamp(
                            device_data[DATA_LAST_GPS_TIME]
                        ),
                        DATA_MODEL_NAME: self._user_data[DATA_USER_BIND_DEVICE][
                            DATA_MODEL_NAME
                        ],
                        DATA_VEHICLE_IMAGE_URL: self._user_data[DATA_USER_BIND_DEVICE][
                            DATA_VEHICLE_IMAGE_URL_VMOTO
                        ],
                    }
                )
            else:
                data.update(
                    {
                        DATA_AGREEMENT_END_TIME: parse_date(
                            self._user_data[DATA_DEVICE][DATA_AGREEMENT_END_TIME]
                        ),
                        DATA_AGREEMENT_START_TIME: parse_date(
                            self._user_data[DATA_DEVICE][DATA_AGREEMENT_START_TIME]
                        ),
                        DATA_LAST_GPS_TIME: parse_date(device_data[DATA_LAST_GPS_TIME]),
                        DATA_LOGO_IMAGE_URL: f"{CDN_BASE_URL}/{self._user_data[DATA_DEVICE][DATA_LOGO_IMAGE_URL]}",
                        DATA_MODEL_NAME: self._user_data[DATA_DEVICE][DATA_MODEL_NAME],
                        DATA_VEHICLE_IMAGE_URL: f"{CDN_BASE_URL}/{self._user_data[DATA_DEVICE][DATA_VEHICLE_IMAGE_URL]}",
                    }
                )

            # Not every API response comes with the "lock" attribute
            if DATA_LOCK in device_data:
                data[DATA_LOCK] = device_data[DATA_LOCK]

            # Check if device is powered on
            self._is_powered_on = data[DATA_POWER_STATUS] == 1

            # Inject home and course data only if vehicle is powered on or moving noticeably
            if self._is_powered_on or self._is_power_off_movement_noticeable(
                data[DATA_LATITUDE], data[DATA_LONGITUDE]
            ):
                # Inject home data
                data.update(
                    self._get_home_data(data[DATA_LATITUDE], data[DATA_LONGITUDE])
                )

                # Inject course data
                data.update(
                    self._get_course_data(data[DATA_LATITUDE], data[DATA_LONGITUDE])
                )

            # ... otherwise use last cached data to reduce GPS jitter
            else:
                _LOGGER.debug(
                    "Current powered off displacement is too small, using last cached data"
                )
                data.update(
                    {
                        DATA_COURSE: self._last_data[DATA_COURSE],
                        DATA_DIR_OF_TRAVEL: self._last_data[DATA_DIR_OF_TRAVEL],
                        DATA_DISTANCE_FROM_HOME: self._last_data[
                            DATA_DISTANCE_FROM_HOME
                        ],
                        DATA_LATITUDE: self._last_data[DATA_LATITUDE],
                        DATA_LONGITUDE: self._last_data[DATA_LONGITUDE],
                        DATA_SPEED: DEFAULT_FLOAT,
                        DATA_WIND_ROSE_COURSE: self._last_data[DATA_WIND_ROSE_COURSE],
                    }
                )

            # Inject additional API data
            data.update(
                await self._get_altitude_data(data[DATA_LATITUDE], data[DATA_LONGITUDE])
            )
            data.update(
                await self._get_reverse_geocoding_data(
                    data[DATA_LATITUDE], data[DATA_LONGITUDE]
                )
            )
            data.update(await self._get_last_trip_data())
            data.update(await self._get_last_warning_data())

            # Cache data
            self._last_data = data

            # Set next update interval
            self._set_update_interval()

            return data
        except ClientResponseError as error:
            if error.status in (400, 2004):
                _LOGGER.exception(
                    "Authentication expired or revoked, please reauthenticate"
                )
                raise ConfigEntryAuthFailed from error
        except Exception as error:
            _LOGGER.exception(error)
            raise UpdateFailed from error

    async def _get_altitude_data(self, latitude: float, longitude: float) -> dict:
        if not self._config_entry.options.get(
            OPT_ENABLE_ALTITUDE_ENTITY, DEFAULT_ENABLE_ALTITUDE_ENTITY
        ):
            _LOGGER.debug("Altitude entity is disabled")
            return {DATA_ALTITUDE: STATE_UNAVAILABLE}

        data = {DATA_ALTITUDE: self._last_data.get(DATA_ALTITUDE, STATE_UNKNOWN)}

        if (
            not self._last_data
            or self._last_data[DATA_ALTITUDE] == STATE_UNAVAILABLE
            or self._last_data[DATA_ALTITUDE] == STATE_UNKNOWN
            or self._is_geo_cache_outdated(latitude, longitude)
        ):
            try:
                _LOGGER.debug("Requesting altitude data")
                res = await self._open_topo_data_api.get_mapzen(latitude, longitude)

                data = {DATA_ALTITUDE: res[DATA_RESULTS][0][DATA_ELEVATION]}
            except Exception as exception:  # pylint: disable=broad-exception-caught
                _LOGGER.exception(exception)
        else:
            _LOGGER.debug("Altitude data is up to date")

        return data

    def _get_home_data(self, latitude: float, longitude: float) -> dict:
        data = {
            DATA_DISTANCE_FROM_HOME: self._last_data.get(
                DATA_DISTANCE_FROM_HOME, STATE_UNKNOWN
            ),
            DATA_DIR_OF_TRAVEL: self._last_data.get(DATA_DIR_OF_TRAVEL, STATE_UNKNOWN),
        }

        home = self._hass.states.get(HOME_ZONE)

        if home:
            home_latitude = home.attributes.get(DATA_LATITUDE)
            home_longitude = home.attributes.get(DATA_LONGITUDE)
            home_radius = round(
                home.attributes.get(DATA_RADIUS) * KM_IN_A_M, DISTANCE_ROUNDING_DECIMALS
            )

            data[DATA_DISTANCE_FROM_HOME] = round(
                calculate_distance(home_latitude, home_longitude, latitude, longitude)
                * KM_IN_A_M,
                DISTANCE_ROUNDING_DECIMALS,
            )

            if data[DATA_DISTANCE_FROM_HOME] <= home_radius:
                data[DATA_DIR_OF_TRAVEL] = DIR_ARRIVED
            elif (
                self._last_data
                and self._last_data[DATA_DISTANCE_FROM_HOME] != STATE_UNKNOWN
            ):
                if (
                    self._last_data[DATA_DISTANCE_FROM_HOME]
                    > data[DATA_DISTANCE_FROM_HOME]
                ):
                    data[DATA_DIR_OF_TRAVEL] = DIR_TOWARDS_HOME
                elif (
                    self._last_data[DATA_DISTANCE_FROM_HOME]
                    < data[DATA_DISTANCE_FROM_HOME]
                ):
                    data[DATA_DIR_OF_TRAVEL] = DIR_AWAY_FROM_HOME
                else:
                    data[DATA_DIR_OF_TRAVEL] = DIR_STATIONARY

        return data

    async def _get_last_trip_data(self) -> dict:
        if not self._config_entry.options.get(
            OPT_ENABLE_LAST_TRIP_ENTITIES, DEFAULT_ENABLE_LAST_TRIP_ENTITIES
        ):
            _LOGGER.debug("Last trip entities are disabled")
            return {
                DATA_LAST_TRIP_RIDE_DISTANCE: STATE_UNAVAILABLE,
                DATA_LAST_TRIP_RIDE_TIME: STATE_UNAVAILABLE,
                DATA_LAST_TRIP_AVG_SPEED: STATE_UNAVAILABLE,
            }

        timestamp = datetime.now().timestamp()
        data = {
            DATA_LAST_TRIP_BEGIN_TIME: self._last_data.get(
                DATA_LAST_TRIP_BEGIN_TIME, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_BEGIN_LATITUDE: self._last_data.get(
                DATA_LAST_TRIP_BEGIN_LATITUDE, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_BEGIN_LONGITUDE: self._last_data.get(
                DATA_LAST_TRIP_BEGIN_LONGITUDE, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_END_TIME: self._last_data.get(
                DATA_LAST_TRIP_END_TIME, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_END_LATITUDE: self._last_data.get(
                DATA_LAST_TRIP_END_LATITUDE, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_END_LONGITUDE: self._last_data.get(
                DATA_LAST_TRIP_END_LONGITUDE, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_RIDE_DISTANCE: self._last_data.get(
                DATA_LAST_TRIP_RIDE_DISTANCE, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_RIDE_TIME: self._last_data.get(
                DATA_LAST_TRIP_RIDE_TIME, STATE_UNKNOWN
            ),
            DATA_LAST_TRIP_AVG_SPEED: self._last_data.get(
                DATA_LAST_TRIP_AVG_SPEED, STATE_UNKNOWN
            ),
        }

        # Do not request data if vehicle is powered on or if current cache is up to date
        if (
            not self._last_data
            or self._last_data[DATA_LAST_TRIP_RIDE_DISTANCE] == STATE_UNAVAILABLE
            or self._last_data[DATA_LAST_TRIP_RIDE_DISTANCE] == STATE_UNKNOWN
            or (
                not self._is_powered_on
                and self._last_trip_timestamp
                and timestamp - self._last_trip_timestamp > LAST_TRIP_CACHE_SECONDS
            )
        ):
            try:
                _LOGGER.debug("Requesting last trip data")

                if self._is_app_vmoto_soco():
                    res = await self._client.get_tracking_history_list(
                        self._user_id, self._device_no, 1, 1
                    )
                    trip = res[DATA_DATA][DATA_DATA][0]

                    data = {
                        DATA_LAST_TRIP_AVG_SPEED: round(
                            trip[DATA_LAST_TRIP_MILEAGE]
                            / trip[DATA_LAST_TRIP_MINUTES]
                            * MINUTES_IN_AN_HOUR,
                            1,
                        ),
                        DATA_LAST_TRIP_BEGIN_TIME: parse_timestamp(
                            trip[DATA_LAST_TRIP_BEGIN_TIME]
                        ),
                        DATA_LAST_TRIP_END_TIME: parse_timestamp(
                            trip[DATA_LAST_TRIP_END_TIME]
                        ),
                        DATA_LAST_TRIP_RIDE_DISTANCE: round(
                            trip[DATA_LAST_TRIP_MILEAGE], DISTANCE_ROUNDING_DECIMALS
                        ),
                        DATA_LAST_TRIP_RIDE_TIME: int(
                            float(trip[DATA_LAST_TRIP_MINUTES]) * SECONDS_IN_A_MINUTE
                        ),
                    }
                else:
                    res = await self._client.get_tracking_history_list(1, 1)
                    trip = res[DATA_DATA][DATA_LIST][0]

                    data = {
                        DATA_LAST_TRIP_AVG_SPEED: trip[DATA_LAST_TRIP_AVG_SPEED],
                        DATA_LAST_TRIP_BEGIN_TIME: parse_date(
                            trip[DATA_LAST_TRIP_BEGIN_TIME]
                        ),
                        DATA_LAST_TRIP_END_TIME: parse_date(
                            trip[DATA_LAST_TRIP_END_TIME]
                        ),
                        DATA_LAST_TRIP_RIDE_DISTANCE: trip[
                            DATA_LAST_TRIP_RIDE_DISTANCE
                        ],
                        DATA_LAST_TRIP_RIDE_TIME: int(
                            float(trip[DATA_LAST_TRIP_RIDE_TIME]) * SECONDS_IN_A_MINUTE
                        ),
                    }

                data.update(
                    {
                        DATA_LAST_TRIP_BEGIN_LATITUDE: str(
                            trip[DATA_LAST_TRIP_BEGIN_LATITUDE]
                        ),
                        DATA_LAST_TRIP_BEGIN_LONGITUDE: str(
                            trip[DATA_LAST_TRIP_BEGIN_LONGITUDE]
                        ),
                        DATA_LAST_TRIP_END_LATITUDE: str(
                            trip[DATA_LAST_TRIP_END_LATITUDE]
                        ),
                        DATA_LAST_TRIP_END_LONGITUDE: str(
                            trip[DATA_LAST_TRIP_END_LONGITUDE]
                        ),
                    }
                )

                self._last_trip_timestamp = timestamp
            except IndexError:
                _LOGGER.debug("Last trip data is empty")
            except Exception as exception:  # pylint: disable=broad-exception-caught
                _LOGGER.exception(exception)
        else:
            _LOGGER.debug("Last trip data is up to date")

        return data

    async def _get_last_warning_data(self) -> dict:
        if not self._config_entry.options.get(
            OPT_ENABLE_LAST_WARNING_ENTITY, DEFAULT_ENABLE_LAST_WARNING_ENTITY
        ):
            _LOGGER.debug("Last warning entity is disabled")
            return {DATA_LAST_WARNING_TIME: STATE_UNAVAILABLE}

        data = {
            DATA_LAST_WARNING_MESSAGE: self._last_data.get(
                DATA_LAST_WARNING_MESSAGE, STATE_UNKNOWN
            ),
            DATA_LAST_WARNING_TIME: self._last_data.get(
                DATA_LAST_WARNING_TIME, STATE_UNKNOWN
            ),
            DATA_LAST_WARNING_TITLE: self._last_data.get(
                DATA_LAST_WARNING_TITLE, STATE_UNKNOWN
            ),
        }

        # Do not request data if vehicle is powered on (it won't generate new warnings)
        if (
            not self._last_data
            or not self._is_powered_on
            or self._last_data[DATA_LAST_WARNING_TIME] == STATE_UNAVAILABLE
            or self._last_data[DATA_LAST_WARNING_TIME] == STATE_UNKNOWN
        ):
            try:
                _LOGGER.debug("Requesting last warning data")
                if self._is_app_vmoto_soco():
                    res = await self._client.get_warning_list(self._user_id, 1, 1)
                    warning = res[DATA_DATA][DATA_DATA][0]

                    data = {
                        DATA_LAST_WARNING_TIME: parse_timestamp(
                            warning[DATA_CREATE_TIME]
                        ),
                    }
                else:
                    res = await self._client.get_warning_list(1, 1)
                    warning = res[DATA_DATA][DATA_LIST][0]

                    data = {
                        DATA_LAST_WARNING_TIME: parse_date(warning[DATA_CREATE_TIME]),
                    }

                data.update(
                    {
                        DATA_LAST_WARNING_MESSAGE: warning[DATA_CONTENT],
                        DATA_LAST_WARNING_TITLE: warning[DATA_TITLE],
                    }
                )
            except IndexError:
                _LOGGER.debug("Last warning data is empty")
            except Exception as exception:  # pylint: disable=broad-exception-caught
                _LOGGER.exception(exception)
        else:
            _LOGGER.debug("Last warning data is up to date")

        return data

    async def _get_reverse_geocoding_data(
        self, latitude: float, longitude: float
    ) -> float:
        if not self._config_entry.options.get(
            OPT_ENABLE_REVERSE_GEOCODING_ENTITY, DEFAULT_ENABLE_REVERSE_GEOCODING_ENTITY
        ):
            _LOGGER.debug("Reverse geocoding entity is disabled")
            return {DATA_REVERSE_GEOCODING: STATE_UNAVAILABLE}

        data = {
            DATA_REVERSE_GEOCODING: self._last_data.get(
                DATA_REVERSE_GEOCODING, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_CITY: self._last_data.get(
                DATA_REVERSE_GEOCODING_CITY, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_COUNTRY: self._last_data.get(
                DATA_REVERSE_GEOCODING_COUNTRY, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_COUNTRY_CODE: self._last_data.get(
                DATA_REVERSE_GEOCODING_COUNTRY_CODE, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_COUNTY: self._last_data.get(
                DATA_REVERSE_GEOCODING_COUNTY, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_HOUSE_NUMBER: self._last_data.get(
                DATA_REVERSE_GEOCODING_HOUSE_NUMBER, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_NEIGHBOURHOOD: self._last_data.get(
                DATA_REVERSE_GEOCODING_NEIGHBOURHOOD, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_POSTCODE: self._last_data.get(
                DATA_REVERSE_GEOCODING_POSTCODE, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_ROAD: self._last_data.get(
                DATA_REVERSE_GEOCODING_ROAD, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_STATE: self._last_data.get(
                DATA_REVERSE_GEOCODING_STATE, STATE_UNKNOWN
            ),
            DATA_REVERSE_GEOCODING_STATE_DISTRICT: self._last_data.get(
                DATA_REVERSE_GEOCODING_STATE_DISTRICT, STATE_UNKNOWN
            ),
        }

        if (
            not self._last_data
            or self._last_data[DATA_REVERSE_GEOCODING] == STATE_UNAVAILABLE
            or self._last_data[DATA_REVERSE_GEOCODING] == STATE_UNKNOWN
            or self._is_geo_cache_outdated(latitude, longitude)
        ):
            try:
                _LOGGER.debug("Requesting reverse geocoding data")
                res = await self._open_street_map_api.get_reverse(latitude, longitude)

                data = {
                    DATA_REVERSE_GEOCODING: res[DATA_DISPLAY_NAME],
                    DATA_REVERSE_GEOCODING_CITY: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_CITY,
                        res[DATA_ADDRESS].get(
                            DATA_REVERSE_GEOCODING_VILLAGE, STATE_UNKNOWN
                        ),
                    ),
                    DATA_REVERSE_GEOCODING_COUNTRY: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_COUNTRY, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_COUNTRY_CODE: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_COUNTRY_CODE, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_COUNTY: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_COUNTY, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_HOUSE_NUMBER: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_HOUSE_NUMBER, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_NEIGHBOURHOOD: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_NEIGHBOURHOOD, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_POSTCODE: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_POSTCODE, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_ROAD: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_ROAD, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_STATE: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_STATE, STATE_UNKNOWN
                    ),
                    DATA_REVERSE_GEOCODING_STATE_DISTRICT: res[DATA_ADDRESS].get(
                        DATA_REVERSE_GEOCODING_STATE_DISTRICT, STATE_UNKNOWN
                    ),
                }
            except Exception as exception:  # pylint: disable=broad-exception-caught
                _LOGGER.exception(exception)
        else:
            _LOGGER.debug("Reverse geocoding data is up to date")

        return data

    def _get_course_data(self, latitude: float, longitude: float) -> dict:
        data = {
            DATA_COURSE: self._last_data.get(DATA_COURSE, DEFAULT_FLOAT),
        }

        if self._last_data:
            data[DATA_COURSE] = calculate_course(
                self._last_data[DATA_LATITUDE],
                self._last_data[DATA_LONGITUDE],
                latitude,
                longitude,
            )

        data[DATA_WIND_ROSE_COURSE] = calculate_wind_rose_course(data[DATA_COURSE])

        return data

    def _is_app_vmoto_soco(self) -> bool:
        return self._config_entry.data.get(CONF_APP_NAME) == VMOTO_SOCO

    def _is_geo_cache_outdated(self, latitude: float, longitude: float) -> bool:
        return (
            not self._last_data
            or round(latitude, API_GEO_PRECISION)
            != round(self._last_data[DATA_LATITUDE], API_GEO_PRECISION)
            or round(longitude, API_GEO_PRECISION)
            != round(self._last_data[DATA_LONGITUDE], API_GEO_PRECISION)
        )

    def _is_power_off_movement_noticeable(
        self, latitude: float, longitude: float
    ) -> bool:
        if not self._last_data:
            return True

        distance = calculate_distance(
            latitude,
            longitude,
            self._last_data[DATA_LATITUDE],
            self._last_data[DATA_LONGITUDE],
        )

        return distance >= POWER_OFF_DISTANCE_THRESHOLD_METERS

    async def set_switch_state(self, data_key: str, state: bool) -> None:
        try:
            if self._is_app_vmoto_soco():
                if data_key == DATA_NATIVE_PUSH_NOTIFICATIONS:
                    await getattr(self._client, SWITCH_API_METHODS[data_key])(
                        self._user_id,
                        state,
                        bool(self._last_data[DATA_NATIVE_TRACKING_HISTORY]),
                    )
                elif data_key == DATA_NATIVE_TRACKING_HISTORY:
                    await getattr(self._client, SWITCH_API_METHODS[data_key])(
                        self._user_id,
                        state,
                        bool(self._last_data[DATA_NATIVE_PUSH_NOTIFICATIONS]),
                    )
                elif data_key == DATA_POWER_STATUS:
                    await getattr(self._client, SWITCH_API_METHODS[data_key])(
                        self._device_no,
                    )
            else:
                await getattr(self._client, SWITCH_API_METHODS[data_key])(state)

            await sleep(SWITCH_REFRESH_SLEEP_SECONDS)
            await self.async_request_refresh()
        except KeyError:
            _LOGGER.debug("Unknown API method for data key: %s", data_key)
        except Exception as exception:  # pylint: disable=broad-exception-caught
            _LOGGER.exception(exception)

    def _set_update_interval(self) -> None:
        # Force a faster update if vehicle is powered on (generating data more often)
        if self._is_powered_on:
            _LOGGER.debug(
                "Power is on, next update will be in %i seconds",
                POWER_ON_UPDATE_SECONDS,
            )
            self.update_interval = timedelta(seconds=POWER_ON_UPDATE_SECONDS)
        else:
            _LOGGER.debug(
                "Power is off, next update will be in %i minute(s)",
                self._initial_update_interval,
            )
            self.update_interval = timedelta(minutes=self._initial_update_interval)
