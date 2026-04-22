from homeassistant.components.device_tracker.const import SourceType
from homeassistant.components.sensor import (
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTime,
)

# Component
DOMAIN = "super_soco_custom"
NAME = "Super Soco Custom"
MANUFACTURER = "Super Soco"
PLATFORMS = [
    "binary_sensor",
    "device_tracker",
    "sensor",
    "switch",
]

# General
API_GEO_PRECISION = 4  # 4 decimals = 11.1 meters
CDN_BASE_URL = "https://oimg.supersocoeg.com:8996"
CONFIG_FLOW_VERSION = 2
COURSE_ROUNDING_DECIMALS = 2
DISTANCE_ROUNDING_DECIMALS = 2
ECU_MAX_VOLTAGE = 6  # It goes from 0 to 6
GPS_MAX_ACCURACY = 15  # It goes from 0 to 15
HOME_ZONE = "zone.home"
KM_IN_A_M = 0.001
LAST_TRIP_CACHE_SECONDS = 600
METERS_IN_EARTH_RADIUS = 6378160
MILLISECONDS_IN_A_SECOND = 1000
MINUTES_IN_AN_HOUR = 60
POWER_OFF_DISTANCE_THRESHOLD_METERS = 16
POWER_ON_UPDATE_SECONDS = 5
SECONDS_IN_A_MINUTE = 60
SIGNAL_MAX_STRENGTH = 4  # It goes from 0 to 4
SUPER_SOCO = "super_soco"
SWITCH_REFRESH_SLEEP_SECONDS = 10
VMOTO_SOCO = "vmoto_soco"

# Directions of travel
DIR_ARRIVED = "arrived"
DIR_AWAY_FROM_HOME = "away_from_home"
DIR_STATIONARY = "stationary"
DIR_TOWARDS_HOME = "towards_home"

# Default coalescing values
DEFAULT_FLOAT = 0.0
DEFAULT_INTEGER = 0
DEFAULT_STRING = ""

# Configuration keys
CONF_APP_NAME = "app_name"
CONF_LOGIN_CODE = "login_code"
CONF_PASSWORD = "password"
CONF_PHONE_NUMBER = "phone_number"
CONF_PHONE_PREFIX = "phone_prefix"
CONF_TOKEN = "token"

# Option keys
OPT_EMAIL = "email"
OPT_ENABLE_ALTITUDE_ENTITY = "enable_altitude_entity"
OPT_ENABLE_LAST_TRIP_ENTITIES = "enable_last_trip_entities"
OPT_ENABLE_LAST_WARNING_ENTITY = "enable_last_warning_entity"
OPT_ENABLE_REVERSE_GEOCODING_ENTITY = "enable_reverse_geocoding_entity"
OPT_UPDATE_INTERVAL = "update_interval"

# Option values
DEFAULT_ENABLE_ALTITUDE_ENTITY = True
DEFAULT_ENABLE_LAST_TRIP_ENTITIES = True
DEFAULT_ENABLE_LAST_WARNING_ENTITY = True
DEFAULT_ENABLE_REVERSE_GEOCODING_ENTITY = False
DEFAULT_UPDATE_INTERVAL_MINUTES = 1
MAX_UPDATE_INTERVAL_MINUTES = 60
MIN_UPDATE_INTERVAL_MINUTES = 1

# Data keys
DATA_ADDRESS = "address"
DATA_AGREEMENT_END_TIME = "agreementEndTime"
DATA_AGREEMENT_START_TIME = "agreemenStartTime"  # Intended typo
DATA_ALTITUDE = "altitude"
DATA_BATTERY = "nowElec"
DATA_CONTENT = "content"
DATA_COURSE = "course"
DATA_CREATE_TIME = "createTime"
DATA_DATA = "data"
DATA_DEVICE = "device"
DATA_DEVICE_NO = "deviceNo"
DATA_DIR_OF_TRAVEL = "dir_of_travel"
DATA_DISPLAY_NAME = "display_name"
DATA_DISTANCE_FROM_HOME = "distance_from_home"
DATA_ECU_BATTERY = "ecuElec"
DATA_ECU_VOLTAGE = "voltage"
DATA_ELEVATION = "elevation"
DATA_ESTIMATED_RANGE = "endurance"
DATA_GPS_ACCURACY = "gps"
DATA_LAST_GPS_TIME = "lastGpsTime"
DATA_LAST_TRIP_AVG_SPEED = "avgSpeed"
DATA_LAST_TRIP_BEGIN_LATITUDE = "beginLatitude"
DATA_LAST_TRIP_BEGIN_LONGITUDE = "beginLongitude"
DATA_LAST_TRIP_BEGIN_TIME = "beginTime"
DATA_LAST_TRIP_END_LATITUDE = "endLatitude"
DATA_LAST_TRIP_END_LONGITUDE = "endLongitude"
DATA_LAST_TRIP_END_TIME = "endTime"
DATA_LAST_TRIP_MILEAGE = "mileage"
DATA_LAST_TRIP_MINUTES = "minutes"
DATA_LAST_TRIP_RIDE_DISTANCE = "rideDistance"
DATA_LAST_TRIP_RIDE_TIME = "rideTime"
DATA_LAST_WARNING_MESSAGE = "lastWarningMessage"
DATA_LAST_WARNING_TIME = "lastWarningTime"
DATA_LAST_WARNING_TITLE = "lastWarningTitle"
DATA_LATITUDE = "latitude"
DATA_LIST = "list"
DATA_LOGO_IMAGE_URL = "logoImg"
DATA_LONGITUDE = "longitude"
DATA_MODEL_NAME = "carModelName"
DATA_NATIVE_PUSH_NOTIFICATIONS = "isWarnPush"
DATA_NATIVE_TRACKING_HISTORY = "historyLocusSwitch"
DATA_POWER_STATUS = "powerStatus"
DATA_POWER_SWITCH = "powerSwitch"
DATA_RADIUS = "radius"
DATA_RESULTS = "results"
DATA_REVERSE_GEOCODING = "reverse_geocoding"
DATA_REVERSE_GEOCODING_CITY = "city"
DATA_REVERSE_GEOCODING_COUNTRY = "country"
DATA_REVERSE_GEOCODING_COUNTRY_CODE = "country_code"
DATA_REVERSE_GEOCODING_COUNTY = "county"
DATA_REVERSE_GEOCODING_HOUSE_NUMBER = "house_number"
DATA_REVERSE_GEOCODING_NEIGHBOURHOOD = "neighbourhood"
DATA_REVERSE_GEOCODING_POSTCODE = "postcode"
DATA_REVERSE_GEOCODING_ROAD = "road"
DATA_REVERSE_GEOCODING_STATE = "state"
DATA_REVERSE_GEOCODING_STATE_DISTRICT = "state_district"
DATA_REVERSE_GEOCODING_VILLAGE = "village"
DATA_SIGNAL_STRENGTH = "gsm"
DATA_SPEED = "sleep"  # Intended typo
DATA_TITLE = "title"
DATA_TRIP_DISTANCE = "mileages"
DATA_USER = "user"
DATA_USER_BIND_DEVICE = "userBindDevice"
DATA_USER_ID = "userId"
DATA_VEHICLE_IMAGE_URL = "imgUrl"
DATA_VEHICLE_IMAGE_URL_VMOTO = "fileUrl"
DATA_WIND_ROSE_COURSE = "wind_rose_course"

# Error keys
ERROR_ALREADY_CONFIGURED = "already_configured"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_UNKNOWN = "unknown"

# Entities
BINARY_SENSORS = [
    (
        "power",  # Id
        DATA_POWER_STATUS,  # Data key
        1,  # Comparison condition
        "mdi:power-standby",  # Icon
        SensorDeviceClass.POWER,  # Device class
        None,  # Extra attributes
    ),
]

DEVICE_TRACKERS = [
    (
        "location",  # Id
        SourceType.GPS,  # Source type
        DATA_LATITUDE,  # Latitude data key
        DATA_LONGITUDE,  # Latitude data key
        DATA_GPS_ACCURACY,  # GPS accuracy data key
        "mdi:mdi:map-marker",  # Icon
        {  # Extra attributes
            "altitude": DATA_ALTITUDE,
            "course": DATA_COURSE,
            "speed": DATA_SPEED,
        },
    ),
]

SENSORS = [
    (
        "agreement_end_time",  # Id
        DATA_AGREEMENT_END_TIME,  # Data key
        None,  # Unit of measurement
        "mdi:calendar-end",  # Icon
        SensorDeviceClass.TIMESTAMP,  # Device class
        None,  # State class
        None,  # Extra attributes
    ),
    (
        "agreement_start_time",
        DATA_AGREEMENT_START_TIME,
        None,
        "mdi:calendar-start",
        SensorDeviceClass.TIMESTAMP,
        None,
        None,
    ),
    (
        "altitude",
        DATA_ALTITUDE,
        UnitOfLength.METERS,
        "mdi:elevation-rise",
        SensorDeviceClass.DISTANCE,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "battery",
        DATA_BATTERY,
        PERCENTAGE,
        "mdi:battery",
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "course",
        DATA_COURSE,
        DEGREE,
        "mdi:compass",
        None,
        None,
        None,
    ),
    (
        "distance_from_home",
        DATA_DISTANCE_FROM_HOME,
        UnitOfLength.KILOMETERS,
        "mdi:home",
        SensorDeviceClass.DISTANCE,
        SensorStateClass.MEASUREMENT,
        {
            "dir_of_travel": DATA_DIR_OF_TRAVEL,
        },
    ),
    (
        "ecu_battery",
        DATA_ECU_BATTERY,
        PERCENTAGE,
        "mdi:battery-charging-wireless",
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "estimated_range",
        DATA_ESTIMATED_RANGE,
        UnitOfLength.KILOMETERS,
        "mdi:map-marker-path",
        SensorDeviceClass.DISTANCE,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "gps_accuracy",
        DATA_GPS_ACCURACY,
        PERCENTAGE,
        "mdi:crosshairs-gps",
        None,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "image",
        DATA_VEHICLE_IMAGE_URL,
        None,
        "mdi:image",
        None,
        None,
        None,
    ),
    (
        "last_gps_time",
        DATA_LAST_GPS_TIME,
        None,
        "mdi:web-clock",
        SensorDeviceClass.TIMESTAMP,
        None,
        None,
    ),
    (
        "last_trip_average_speed",
        DATA_LAST_TRIP_AVG_SPEED,
        UnitOfSpeed.KILOMETERS_PER_HOUR,
        "mdi:speedometer",
        SensorDeviceClass.SPEED,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "last_trip_distance",
        DATA_LAST_TRIP_RIDE_DISTANCE,
        UnitOfLength.KILOMETERS,
        "mdi:map-marker-distance",
        SensorDeviceClass.DISTANCE,
        SensorStateClass.MEASUREMENT,
        {
            "begin_latitude": DATA_LAST_TRIP_BEGIN_LATITUDE,
            "begin_longitude": DATA_LAST_TRIP_BEGIN_LONGITUDE,
            "end_latitude": DATA_LAST_TRIP_END_LATITUDE,
            "end_longitude": DATA_LAST_TRIP_END_LONGITUDE,
        },
    ),
    (
        "last_trip_duration",
        DATA_LAST_TRIP_RIDE_TIME,
        UnitOfTime.SECONDS,
        "mdi:timer",
        SensorDeviceClass.DURATION,
        SensorStateClass.MEASUREMENT,
        {
            "begin_time": DATA_LAST_TRIP_BEGIN_TIME,
            "end_time": DATA_LAST_TRIP_END_TIME,
        },
    ),
    (
        "last_warning",
        DATA_LAST_WARNING_TIME,
        None,
        "mdi:alert-circle",
        SensorDeviceClass.TIMESTAMP,
        None,
        {
            "message": DATA_LAST_WARNING_MESSAGE,
            "title": DATA_LAST_WARNING_TITLE,
        },
    ),
    (
        "logo",
        DATA_LOGO_IMAGE_URL,
        None,
        "mdi:image",
        None,
        None,
        None,
    ),
    (
        "reverse_geocoding",
        DATA_REVERSE_GEOCODING,
        None,
        "mdi:map",
        None,
        None,
        {
            "city": DATA_REVERSE_GEOCODING_CITY,
            "country": DATA_REVERSE_GEOCODING_COUNTRY,
            "country_code": DATA_REVERSE_GEOCODING_COUNTRY_CODE,
            "county": DATA_REVERSE_GEOCODING_COUNTY,
            "house_number": DATA_REVERSE_GEOCODING_HOUSE_NUMBER,
            "neighborhood": DATA_REVERSE_GEOCODING_NEIGHBOURHOOD,
            "postcode": DATA_REVERSE_GEOCODING_POSTCODE,
            "road": DATA_REVERSE_GEOCODING_ROAD,
            "state": DATA_REVERSE_GEOCODING_STATE,
            "state_district": DATA_REVERSE_GEOCODING_STATE_DISTRICT,
        },
    ),
    (
        "signal_strength",
        DATA_SIGNAL_STRENGTH,
        PERCENTAGE,
        "mdi:signal",
        None,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "speed",
        DATA_SPEED,
        UnitOfSpeed.KILOMETERS_PER_HOUR,
        "mdi:speedometer",
        SensorDeviceClass.SPEED,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    (
        "trip_distance",
        DATA_TRIP_DISTANCE,
        UnitOfLength.KILOMETERS,
        "mdi:map-marker-distance",
        SensorDeviceClass.DISTANCE,
        SensorStateClass.TOTAL_INCREASING,
        None,
    ),
    (
        "wind_rose_course",
        DATA_WIND_ROSE_COURSE,
        None,
        "mdi:compass-rose",
        None,
        None,
        None,
    ),
]

SWITCHES = [
    (
        "native_push_notifications",  # Id
        DATA_NATIVE_PUSH_NOTIFICATIONS,  # Data key
        1,  # Comparison condition
        "mdi:bell-ring",  # Icon
        None,  # Extra attributes
    ),
    (
        "native_tracking_history",
        DATA_NATIVE_TRACKING_HISTORY,
        1,
        "mdi:database-marker",
        None,
    ),
    (
        "power",
        DATA_POWER_SWITCH,
        1,
        "mdi:power-standby",
        None,
    ),
]

# Switch API methods
SWITCH_API_METHODS = {
    DATA_NATIVE_PUSH_NOTIFICATIONS: "set_push_notifications",
    DATA_NATIVE_TRACKING_HISTORY: "set_tracking_history",
    DATA_POWER_SWITCH: "switch_power",
}

# Phone prefixes
PHONE_PREFIXES = [
    ["Afghanistan (93)", 93],
    ["Albania (355)", 355],
    ["Algeria (213)", 213],
    ["American Samoa (1684)", 1684],
    ["Andorra (376)", 376],
    ["Angola (244)", 244],
    ["Anguilla (1264)", 1264],
    ["Antigua and Barbuda (1268)", 1268],
    ["Argentina (54)", 54],
    ["Armenia (374)", 374],
    ["Aruba (297)", 297],
    ["Australia (61)", 61],
    ["Austria (43)", 43],
    ["Azerbaijan (994)", 994],
    ["Bahamas (1242)", 1242],
    ["Bahrain (973)", 973],
    ["Bangladesh (880)", 880],
    ["Barbados (1246)", 1246],
    ["Belarus (375)", 375],
    ["Belgium (32)", 32],
    ["Belize (501)", 501],
    ["Benin (229)", 229],
    ["Bermuda (1441)", 1441],
    ["Bhutan (975)", 975],
    ["Bolivia (591)", 591],
    ["Bosnia and Herzegovina (387)", 387],
    ["Botswana (267)", 267],
    ["Brazil (55)", 55],
    ["Brunei (673)", 673],
    ["Bulgaria (359)", 359],
    ["Burkina Faso (226)", 226],
    ["Burundi (257)", 257],
    ["Cambodia (855)", 855],
    ["Cameroon (237)", 237],
    ["Canada (1)", 1],
    ["Cape Verde (238)", 238],
    ["Cayman Islands (1345)", 1345],
    ["Central African Republic (236)", 236],
    ["Chad (235)", 235],
    ["Chile (56)", 56],
    ["China (86)", 86],
    ["Colombia (57)", 57],
    ["Comoros (269)", 269],
    ["Cook Islands (682)", 682],
    ["Costa Rica (506)", 506],
    ["Croatia (385)", 385],
    ["Cuba (53)", 53],
    ["Curacao (599)", 599],
    ["Cyprus (357)", 357],
    ["Czech (420)", 420],
    ["Democratic Republic of the Congo (243)", 243],
    ["Denmark (45)", 45],
    ["Djibouti (253)", 253],
    ["Dominica (1767)", 1767],
    ["Dominican Republic (1809)", 1809],
    ["East Timor (670)", 670],
    ["Ecuador (593)", 593],
    ["Egypt (20)", 20],
    ["El Salvador (503)", 503],
    ["Equatorial Guinea (240)", 240],
    ["Eritrea (291)", 291],
    ["Estonia (372)", 372],
    ["Ethiopia (251)", 251],
    ["Faroe Islands (298)", 298],
    ["Fiji (679)", 679],
    ["Finland (358)", 358],
    ["France (33)", 33],
    ["French Guiana (594)", 594],
    ["French Polynesia (689)", 689],
    ["Gabon (241)", 241],
    ["Gambia (220)", 220],
    ["Georgia (995)", 995],
    ["Germany (49)", 49],
    ["Ghana (233)", 233],
    ["Gibraltar (350)", 350],
    ["Greece (30)", 30],
    ["Greenland (299)", 299],
    ["Grenada (1473)", 1473],
    ["Guadeloupe (590)", 590],
    ["Guam (1671)", 1671],
    ["Guatemala (502)", 502],
    ["Guinea (224)", 224],
    ["Guinea-Bissau (245)", 245],
    ["Guyana (592)", 592],
    ["Haiti (509)", 509],
    ["Honduras (504)", 504],
    ["Hong Kong (852)", 852],
    ["Hungary (36)", 36],
    ["Iceland (354)", 354],
    ["India (91)", 91],
    ["Indonesia (62)", 62],
    ["Iran (98)", 98],
    ["Iraq (964)", 964],
    ["Ireland (353)", 353],
    ["Israel (972)", 972],
    ["Italy (39)", 39],
    ["Ivory Coast (225)", 225],
    ["Jamaica (1876)", 1876],
    ["Japan (81)", 81],
    ["Jordan (962)", 962],
    ["Kazakhstan (7)", 7],
    ["Kenya (254)", 254],
    ["Kiribati (686)", 686],
    ["Kuwait (965)", 965],
    ["Kyrgyzstan (996)", 996],
    ["Laos (856)", 856],
    ["Latvia (371)", 371],
    ["Lebanon (961)", 961],
    ["Lesotho (266)", 266],
    ["Liberia (231)", 231],
    ["Libya (218)", 218],
    ["Liechtenstein (423)", 423],
    ["Lithuania (370)", 370],
    ["Luxembourg (352)", 352],
    ["Macau (853)", 853],
    ["Macedonia (389)", 389],
    ["Madagascar (261)", 261],
    ["Malawi (265)", 265],
    ["Malaysia (60)", 60],
    ["Maldives (960)", 960],
    ["Mali (223)", 223],
    ["Malta (356)", 356],
    ["Martinique (596)", 596],
    ["Mauritania (222)", 222],
    ["Mauritius (230)", 230],
    ["Mayotte (269)", 269],
    ["Mexico (52)", 52],
    ["Moldova (373)", 373],
    ["Monaco (377)", 377],
    ["Mongolia (976)", 976],
    ["Montenegro (382)", 382],
    ["Montserrat (1664)", 1664],
    ["Morocco (212)", 212],
    ["Mozambique (258)", 258],
    ["Myanmar (95)", 95],
    ["Namibia (264)", 264],
    ["Nepal (977)", 977],
    ["Netherlands (31)", 31],
    ["New Caledonia (687)", 687],
    ["New Zealand (64)", 64],
    ["Nicaragua (505)", 505],
    ["Niger (227)", 227],
    ["Nigeria (234)", 234],
    ["Norway (47)", 47],
    ["Oman (968)", 968],
    ["Pakistan (92)", 92],
    ["Palau (680)", 680],
    ["Palestine (970)", 970],
    ["Panama (507)", 507],
    ["Papua New Guinea (675)", 675],
    ["Paraguay (595)", 595],
    ["Peru (51)", 51],
    ["Philippines (63)", 63],
    ["Poland (48)", 48],
    ["Portugal (351)", 351],
    ["Puerto Rico (1787)", 1787],
    ["Qatar (974)", 974],
    ["Republic Of The Congo (242)", 242],
    ["Réunion Island (262)", 262],
    ["Romania (40)", 40],
    ["Russia (7)", 7],
    ["Rwanda (250)", 250],
    ["Saint Kitts and Nevis (1869)", 1869],
    ["Saint Lucia (1758)", 1758],
    ["Saint Pierre and Miquelon (508)", 508],
    ["Saint Vincent and The Grenadines (1784)", 1784],
    ["Samoa (685)", 685],
    ["San Marino (378)", 378],
    ["Sao Tome and Principe (239)", 239],
    ["Saudi Arabia (966)", 966],
    ["Senegal (221)", 221],
    ["Serbia (381)", 381],
    ["Seychelles (248)", 248],
    ["Sierra Leone (232)", 232],
    ["Singapore (65)", 65],
    ["Sint Maarten(Dutch Part) (1721)", 1721],
    ["Slovakia (421)", 421],
    ["Slovenia (386)", 386],
    ["Solomon Islands (677)", 677],
    ["Somalia (252)", 252],
    ["South Africa (27)", 27],
    ["South Korea (82)", 82],
    ["Spain (34)", 34],
    ["Sri Lanka (94)", 94],
    ["Sudan (249)", 249],
    ["Suriname (597)", 597],
    ["Swaziland (268)", 268],
    ["Sweden (46)", 46],
    ["Switzerland (41)", 41],
    ["Syria (963)", 963],
    ["Taiwan (886)", 886],
    ["Tajikistan (992)", 992],
    ["Tanzania (255)", 255],
    ["Thailand (66)", 66],
    ["Togo (228)", 228],
    ["Tonga (676)", 676],
    ["Trinidad and Tobago (1868)", 1868],
    ["Tunisia (216)", 216],
    ["Turkey (90)", 90],
    ["Turkmenistan (993)", 993],
    ["Turks and Caicos Islands (1649)", 1649],
    ["Uganda (256)", 256],
    ["Ukraine (380)", 380],
    ["United Arab Emirates (971)", 971],
    ["United Kingdom (44)", 44],
    ["United States (1)", 1],
    ["Uruguay (598)", 598],
    ["Uzbekistan (998)", 998],
    ["Vanuatu (678)", 678],
    ["Venezuela (58)", 58],
    ["Vietnam (84)", 84],
    ["Virgin Islands,British (1340)", 1340],
    ["Virgin Islands,US (1284)", 1284],
    ["Yemen (967)", 967],
    ["Zambia (260)", 260],
    ["Zimbabwe (263)", 263],
]

# App names
APP_NAMES = {
    SUPER_SOCO: "Super Soco",
    VMOTO_SOCO: "Vmoto Soco",
}
