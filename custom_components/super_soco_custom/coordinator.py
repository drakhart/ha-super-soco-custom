import logging

from datetime import datetime, timedelta

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_GEO_PRECISION,
    CDN_BASE_URL,
    DATA_ACCUMULATIVE_RIM,
    DATA_ADDRESS,
    DATA_AGREEMENT_END_TIME,
    DATA_AGREEMENT_START_TIME,
    DATA_ALTITUDE,
    DATA_BATTERY_PERCENTAGE,
    DATA_CONTENT,
    DATA_COURSE,
    DATA_CREATE_TIME,
    DATA_DATA,
    DATA_DEVICE_NUMBER,
    DATA_DEVICE,
    DATA_DIR_OF_TRAVEL,
    DATA_DISPLAY_NAME,
    DATA_DISTANCE_FROM_HOME,
    DATA_ELEVATION,
    DATA_ESTIMATED_RANGE,
    DATA_REVERSE_GEOCODING,
    DATA_REVERSE_GEOCODING_CITY,
    DATA_REVERSE_GEOCODING_COUNTRY,
    DATA_REVERSE_GEOCODING_COUNTRY_CODE,
    DATA_REVERSE_GEOCODING_COUNTY,
    DATA_REVERSE_GEOCODING_HOUSE_NUMBER,
    DATA_REVERSE_GEOCODING_NEIGHBOURHOOD,
    DATA_REVERSE_GEOCODING_POSTCODE,
    DATA_REVERSE_GEOCODING_ROAD,
    DATA_REVERSE_GEOCODING_STATE,
    DATA_REVERSE_GEOCODING_STATE_DISTRICT,
    DATA_REVERSE_GEOCODING_VILLAGE,
    DATA_GPS_ACCURACY,
    DATA_LAST_GPS_TIME,
    DATA_LAST_TRIP_BEGIN_LATITUDE,
    DATA_LAST_TRIP_BEGIN_LONGITUDE,
    DATA_LAST_TRIP_BEGIN_TIME,
    DATA_LAST_TRIP_END_LATITUDE,
    DATA_LAST_TRIP_END_LONGITUDE,
    DATA_LAST_TRIP_END_TIME,
    DATA_LAST_TRIP_RIDE_DISTANCE,
    DATA_LAST_TRIP_RIDE_SPEED,
    DATA_LAST_TRIP_RIDE_TIME,
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
    DATA_SIGNAL_STRENGTH,
    DATA_SLEEP,
    DATA_SPEED,
    DATA_TIMESTAMP,
    DATA_TITLE,
    DATA_TRIP_DISTANCE,
    DATA_VEHICLE_IMAGE_URL,
    DATA_VOLTAGE,
    DATA_LAST_WARNING_MESSAGE,
    DATA_LAST_WARNING_TIME,
    DATA_LAST_WARNING_TITLE,
    DATA_WIND_ROSE_COURSE,
    DEFAULT_ENABLE_REVERSE_GEOCODING_ENTITY,
    DEFAULT_ENABLE_LAST_TRIP_ENTITIES,
    DEFAULT_ENABLE_LAST_WARNING_ENTITY,
    DEFAULT_FLOAT,
    DEFAULT_ENABLE_ALTITUDE_ENTITY,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DIR_ARRIVED,
    DIR_AWAY_FROM_HOME,
    DIR_STATIONARY,
    DIR_TOWARDS_HOME,
    DISTANCE_ROUNDING_ZEROES,
    DOMAIN,
    HOME_ZONE,
    KM_IN_A_M,
    KMH_IN_A_MS,
    LAST_TRIP_CACHE_SECONDS,
    OPT_ENABLE_ALTITUDE_ENTITY,
    OPT_ENABLE_REVERSE_GEOCODING_ENTITY,
    OPT_ENABLE_LAST_TRIP_ENTITIES,
    OPT_ENABLE_LAST_WARNING_ENTITY,
    OPT_UPDATE_INTERVAL,
    POWER_ON_UPDATE_SECONDS,
    SECONDS_IN_A_MINUTE,
    SPEED_ROUNDING_ZEROES,
    SPEED_THRESHOLD_KMH,
    SWITCH_API_METHODS,
)
from .helpers import (
    calculate_course,
    calculate_distance,
    calculate_wind_rose_course,
    parse_date,
)
from .open_street_map_api import OpenStreetMapAPI
from .open_topo_data_api import OpenTopoDataAPI
from .super_soco_api import SuperSocoAPI

_LOGGER: logging.Logger = logging.getLogger(__package__)


class SuperSocoCustomDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        super_soco_api: SuperSocoAPI,
        open_street_map_api: OpenStreetMapAPI,
        open_topo_data_api: OpenTopoDataAPI,
    ) -> None:
        self._hass = hass
        self._config_entry = config_entry
        self._super_soco_api = super_soco_api
        self._open_street_map_api = open_street_map_api
        self._open_topo_data_api = open_topo_data_api
        self._last_data = {}
        self._initial_update_interval = int(
            config_entry.options.get(
                OPT_UPDATE_INTERVAL,
                DEFAULT_UPDATE_INTERVAL_MINUTES,
            )
        )

        _LOGGER.debug(
            f"Setting initial update interval: {self._initial_update_interval} minute(s)"
        )
        update_interval = timedelta(minutes=self._initial_update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        try:
            # Build main data
            if not hasattr(self, "_user_data"):
                _LOGGER.debug("Requesting user data for the 1st time")
                self._user_data = (await self._super_soco_api.get_user())[DATA_DATA]

            _LOGGER.debug("Requesting device data")
            device_data = (
                await self._super_soco_api.get_device(
                    self._user_data[DATA_DEVICE][DATA_DEVICE_NUMBER]
                )
            )[DATA_DATA]

            data = {
                DATA_ACCUMULATIVE_RIM: device_data[DATA_ACCUMULATIVE_RIM],
                DATA_AGREEMENT_END_TIME: parse_date(
                    self._user_data[DATA_DEVICE][DATA_AGREEMENT_END_TIME]
                ),
                DATA_AGREEMENT_START_TIME: parse_date(
                    self._user_data[DATA_DEVICE][DATA_AGREEMENT_START_TIME]
                ),
                DATA_BATTERY_PERCENTAGE: device_data[DATA_BATTERY_PERCENTAGE],
                DATA_TRIP_DISTANCE: round(
                    device_data[DATA_TRIP_DISTANCE], DISTANCE_ROUNDING_ZEROES
                ),
                DATA_ESTIMATED_RANGE: device_data[DATA_ESTIMATED_RANGE],
                DATA_GPS_ACCURACY: device_data[DATA_GPS_ACCURACY],
                DATA_LAST_GPS_TIME: parse_date(device_data[DATA_LAST_GPS_TIME]),
                DATA_LATITUDE: device_data[DATA_LATITUDE],
                DATA_LOGO_IMAGE_URL: f"{CDN_BASE_URL}/{self._user_data[DATA_DEVICE][DATA_LOGO_IMAGE_URL]}",
                DATA_LONGITUDE: device_data[DATA_LONGITUDE],
                DATA_MODEL_NAME: self._user_data[DATA_DEVICE][DATA_MODEL_NAME],
                DATA_NATIVE_PUSH_NOTIFICATIONS: device_data[
                    DATA_NATIVE_PUSH_NOTIFICATIONS
                ],
                DATA_NATIVE_TRACKING_HISTORY: device_data[DATA_NATIVE_TRACKING_HISTORY],
                DATA_POWER_STATUS: device_data[DATA_POWER_STATUS],
                DATA_SIGNAL_STRENGTH: device_data[DATA_SIGNAL_STRENGTH],
                DATA_SLEEP: device_data[DATA_SLEEP],
                DATA_VEHICLE_IMAGE_URL: f"{CDN_BASE_URL}/{self._user_data[DATA_DEVICE][DATA_VEHICLE_IMAGE_URL]}",
                DATA_VOLTAGE: device_data[DATA_VOLTAGE],
            }

            # Not every API response comes with the "lock" attribute
            if DATA_LOCK in device_data:
                data[DATA_LOCK] = device_data[DATA_LOCK]

            # Check if device is powered on
            self._is_powered_on = data[DATA_POWER_STATUS] == 1

            # Inject speed, course and distance data
            data.update(self._get_home_data(data[DATA_LATITUDE], data[DATA_LONGITUDE]))
            data.update(
                self._get_speed_and_course_data(
                    data[DATA_LATITUDE], data[DATA_LONGITUDE]
                )
            )

            # Inject timestamp depending on last vs current position
            data.update(
                self._get_timestamp_data(data[DATA_LATITUDE], data[DATA_LONGITUDE])
            )

            # Reduce GPS jitter if vehicle is still
            if self._last_data and data[DATA_SPEED] < SPEED_THRESHOLD_KMH:
                _LOGGER.debug(
                    f"Current speed is lower than threshold, using last data ({data[DATA_SPEED]} < {SPEED_THRESHOLD_KMH})"
                )
                data.update(
                    {
                        DATA_COURSE: self._last_data[DATA_COURSE],
                        DATA_LATITUDE: self._last_data[DATA_LATITUDE],
                        DATA_LONGITUDE: self._last_data[DATA_LONGITUDE],
                        DATA_SPEED: DEFAULT_FLOAT,
                    }
                )

            # Inject wind rose data
            data[DATA_WIND_ROSE_COURSE] = calculate_wind_rose_course(data[DATA_COURSE])

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
        except Exception as exception:
            _LOGGER.exception(exception)
            raise UpdateFailed() from exception

    async def _get_altitude_data(self, latitude: float, longitude: float) -> float:
        if not self._config_entry.options.get(
            OPT_ENABLE_ALTITUDE_ENTITY, DEFAULT_ENABLE_ALTITUDE_ENTITY
        ):
            _LOGGER.debug("Altitude entity is disabled")
            return {DATA_ALTITUDE: STATE_UNAVAILABLE}

        data = {DATA_ALTITUDE: self._last_data.get(DATA_ALTITUDE, STATE_UNKNOWN)}

        if (
            not self._last_data
            or self._last_data[DATA_ALTITUDE] == STATE_UNAVAILABLE
            or self._is_geo_cache_outdated(latitude, longitude)
        ):
            try:
                _LOGGER.debug("Requesting altitude data")
                res = await self._open_topo_data_api.get_mapzen(latitude, longitude)

                data = {DATA_ALTITUDE: res[DATA_RESULTS][0][DATA_ELEVATION]}
            except Exception as exception:
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
                home.attributes.get(DATA_RADIUS) * KM_IN_A_M, DISTANCE_ROUNDING_ZEROES
            )

            data[DATA_DISTANCE_FROM_HOME] = round(
                calculate_distance(home_latitude, home_longitude, latitude, longitude)
                * KM_IN_A_M,
                DISTANCE_ROUNDING_ZEROES,
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
                DATA_LAST_TRIP_RIDE_SPEED: STATE_UNAVAILABLE,
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
            DATA_LAST_TRIP_RIDE_SPEED: self._last_data.get(
                DATA_LAST_TRIP_RIDE_SPEED, STATE_UNKNOWN
            ),
        }

        # Do not request data if vehicle is powered on or if current cache is up to date
        if (
            not self._last_data
            or self._last_data[DATA_LAST_TRIP_RIDE_DISTANCE] == STATE_UNAVAILABLE
            or (
                not self._is_powered_on
                and hasattr(self, "_last_trip_timestamp")
                and timestamp - self._last_trip_timestamp > LAST_TRIP_CACHE_SECONDS
            )
        ):
            try:
                _LOGGER.debug("Requesting last trip data")
                res = (await self._super_soco_api.get_tracking_history_list(1, 1))[
                    DATA_DATA
                ]

                data = {
                    DATA_LAST_TRIP_BEGIN_TIME: parse_date(
                        res[DATA_LIST][0][DATA_LAST_TRIP_BEGIN_TIME]
                    ),
                    DATA_LAST_TRIP_BEGIN_LATITUDE: str(
                        res[DATA_LIST][0][DATA_LAST_TRIP_BEGIN_LATITUDE]
                    ),
                    DATA_LAST_TRIP_BEGIN_LONGITUDE: str(
                        res[DATA_LIST][0][DATA_LAST_TRIP_BEGIN_LONGITUDE]
                    ),
                    DATA_LAST_TRIP_END_TIME: parse_date(
                        res[DATA_LIST][0][DATA_LAST_TRIP_END_TIME]
                    ),
                    DATA_LAST_TRIP_END_LATITUDE: str(
                        res[DATA_LIST][0][DATA_LAST_TRIP_END_LATITUDE]
                    ),
                    DATA_LAST_TRIP_END_LONGITUDE: str(
                        res[DATA_LIST][0][DATA_LAST_TRIP_END_LONGITUDE]
                    ),
                    DATA_LAST_TRIP_RIDE_DISTANCE: res[DATA_LIST][0][
                        DATA_LAST_TRIP_RIDE_DISTANCE
                    ],
                    DATA_LAST_TRIP_RIDE_TIME: float(
                        res[DATA_LIST][0][DATA_LAST_TRIP_RIDE_TIME]
                    )
                    * SECONDS_IN_A_MINUTE,
                    DATA_LAST_TRIP_RIDE_SPEED: res[DATA_LIST][0][
                        DATA_LAST_TRIP_RIDE_SPEED
                    ],
                }

                self._last_trip_timestamp = timestamp
            except IndexError:
                _LOGGER.debug("Last trip data is empty")
                pass
            except Exception as exception:
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
        ):
            try:
                _LOGGER.debug("Requesting last warning data")
                res = (await self._super_soco_api.get_warning_list(1, 1))[DATA_DATA]

                data = {
                    DATA_LAST_WARNING_MESSAGE: res[DATA_LIST][0][DATA_CONTENT],
                    DATA_LAST_WARNING_TIME: parse_date(
                        res[DATA_LIST][0][DATA_CREATE_TIME]
                    ),
                    DATA_LAST_WARNING_TITLE: res[DATA_LIST][0][DATA_TITLE],
                }
            except IndexError:
                _LOGGER.debug("Last warning data is empty")
                pass
            except Exception as exception:
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
            except Exception as exception:
                _LOGGER.exception(exception)
        else:
            _LOGGER.debug("Reverse geocoding data is up to date")

        return data

    def _get_speed_and_course_data(self, latitude: float, longitude: float) -> dict:
        data = {
            DATA_COURSE: self._last_data.get(DATA_COURSE, DEFAULT_FLOAT),
            DATA_SPEED: self._last_data.get(DATA_SPEED, DEFAULT_FLOAT),
        }

        if self._last_data:
            dist_m = calculate_distance(
                self._last_data[DATA_LATITUDE],
                self._last_data[DATA_LONGITUDE],
                latitude,
                longitude,
            )
            time_s = datetime.now().timestamp() - self._last_data[DATA_TIMESTAMP]

            data[DATA_SPEED] = round(
                dist_m / time_s * KMH_IN_A_MS, SPEED_ROUNDING_ZEROES
            )
            data[DATA_COURSE] = calculate_course(
                self._last_data[DATA_LATITUDE],
                self._last_data[DATA_LONGITUDE],
                latitude,
                longitude,
            )

        return data

    def _get_timestamp_data(self, latitude: float, longitude: float) -> dict:
        data = {
            DATA_TIMESTAMP: datetime.now().timestamp(),
        }

        if (
            self._last_data
            and latitude == self._last_data[DATA_LATITUDE]
            and longitude == self._last_data[DATA_LONGITUDE]
        ):
            data = {
                DATA_TIMESTAMP: self._last_data[DATA_TIMESTAMP],
            }

        return data

    def _is_geo_cache_outdated(self, latitude: float, longitude: float) -> bool:
        return (
            not self._last_data
            or round(latitude, API_GEO_PRECISION)
            != round(self._last_data[DATA_LATITUDE], API_GEO_PRECISION)
            or round(longitude, API_GEO_PRECISION)
            != round(self._last_data[DATA_LONGITUDE], API_GEO_PRECISION)
        )

    async def set_switch_state(self, data_key: str, state: bool) -> None:
        try:
            await getattr(self._super_soco_api, SWITCH_API_METHODS[data_key])(state)
            await self.async_request_refresh()
        except KeyError:
            _LOGGER.debug(f"Unknown API method for data key: {data_key}")
        except Exception as exception:
            _LOGGER.exception(exception)

    def _set_update_interval(self) -> None:
        # Force a faster update if vehicle is powered on (generating data more often)
        if self._is_powered_on:
            _LOGGER.debug(
                f"Power is on, next update will be in {POWER_ON_UPDATE_SECONDS} seconds"
            )
            self.update_interval = timedelta(seconds=POWER_ON_UPDATE_SECONDS)
        else:
            _LOGGER.debug(
                f"Power is off, next update will be in {self._initial_update_interval} minute(s)"
            )
            self.update_interval = timedelta(minutes=self._initial_update_interval)
