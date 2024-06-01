from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
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
        SOURCE_TYPE_GPS,  # Source type
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
PHONE_PREFIXES = {  # pylint: disable=duplicate-key
    93: "Afghanistan (93)",
    355: "Albania (355)",
    213: "Algeria (213)",
    1684: "American Samoa (1684)",
    376: "Andorra (376)",
    244: "Angola (244)",
    1264: "Anguilla (1264)",
    1268: "Antigua and Barbuda (1268)",
    54: "Argentina (54)",
    374: "Armenia (374)",
    297: "Aruba (297)",
    61: "Australia (61)",
    43: "Austria (43)",
    994: "Azerbaijan (994)",
    1242: "Bahamas (1242)",
    973: "Bahrain (973)",
    880: "Bangladesh (880)",
    1246: "Barbados (1246)",
    375: "Belarus (375)",
    32: "Belgium (32)",
    501: "Belize (501)",
    229: "Benin (229)",
    1441: "Bermuda (1441)",
    975: "Bhutan (975)",
    591: "Bolivia (591)",
    387: "Bosnia and Herzegovina (387)",
    267: "Botswana (267)",
    55: "Brazil (55)",
    673: "Brunei (673)",
    359: "Bulgaria (359)",
    226: "Burkina Faso (226)",
    257: "Burundi (257)",
    855: "Cambodia (855)",
    237: "Cameroon (237)",
    1: "Canada (1)",
    238: "Cape Verde (238)",
    1345: "Cayman Islands (1345)",
    236: "Central African Republic (236)",
    235: "Chad (235)",
    56: "Chile (56)",
    86: "China (86)",
    57: "Colombia (57)",
    269: "Comoros (269)",
    682: "Cook Islands (682)",
    506: "Costa Rica (506)",
    385: "Croatia (385)",
    53: "Cuba (53)",
    599: "Curacao (599)",
    357: "Cyprus (357)",
    420: "Czech (420)",
    243: "Democratic Republic of the Congo (243)",
    45: "Denmark (45)",
    253: "Djibouti (253)",
    1767: "Dominica (1767)",
    1809: "Dominican Republic (1809)",
    670: "East Timor (670)",
    593: "Ecuador (593)",
    20: "Egypt (20)",
    503: "El Salvador (503)",
    240: "Equatorial Guinea (240)",
    291: "Eritrea (291)",
    372: "Estonia (372)",
    251: "Ethiopia (251)",
    298: "Faroe Islands (298)",
    679: "Fiji (679)",
    358: "Finland (358)",
    33: "France (33)",
    594: "French Guiana (594)",
    689: "French Polynesia (689)",
    241: "Gabon (241)",
    220: "Gambia (220)",
    995: "Georgia (995)",
    49: "Germany (49)",
    233: "Ghana (233)",
    350: "Gibraltar (350)",
    30: "Greece (30)",
    299: "Greenland (299)",
    1473: "Grenada (1473)",
    590: "Guadeloupe (590)",
    1671: "Guam (1671)",
    502: "Guatemala (502)",
    224: "Guinea (224)",
    245: "Guinea-Bissau (245)",
    592: "Guyana (592)",
    509: "Haiti (509)",
    504: "Honduras (504)",
    852: "Hong Kong (852)",
    36: "Hungary (36)",
    354: "Iceland (354)",
    91: "India (91)",
    62: "Indonesia (62)",
    98: "Iran (98)",
    964: "Iraq (964)",
    353: "Ireland (353)",
    972: "Israel (972)",
    39: "Italy (39)",
    225: "Ivory Coast (225)",
    1876: "Jamaica (1876)",
    81: "Japan (81)",
    962: "Jordan (962)",
    7: "Kazakhstan (7)",
    254: "Kenya (254)",
    686: "Kiribati (686)",
    965: "Kuwait (965)",
    996: "Kyrgyzstan (996)",
    856: "Laos (856)",
    371: "Latvia (371)",
    961: "Lebanon (961)",
    266: "Lesotho (266)",
    231: "Liberia (231)",
    218: "Libya (218)",
    423: "Liechtenstein (423)",
    370: "Lithuania (370)",
    352: "Luxembourg (352)",
    853: "Macau (853)",
    389: "Macedonia (389)",
    261: "Madagascar (261)",
    265: "Malawi (265)",
    60: "Malaysia (60)",
    960: "Maldives (960)",
    223: "Mali (223)",
    356: "Malta (356)",
    596: "Martinique (596)",
    222: "Mauritania (222)",
    230: "Mauritius (230)",
    269: "Mayotte (269)",
    52: "Mexico (52)",
    373: "Moldova (373)",
    377: "Monaco (377)",
    976: "Mongolia (976)",
    382: "Montenegro (382)",
    1664: "Montserrat (1664)",
    212: "Morocco (212)",
    258: "Mozambique (258)",
    95: "Myanmar (95)",
    264: "Namibia (264)",
    977: "Nepal (977)",
    31: "Netherlands (31)",
    687: "New Caledonia (687)",
    64: "New Zealand (64)",
    505: "Nicaragua (505)",
    227: "Niger (227)",
    234: "Nigeria (234)",
    47: "Norway (47)",
    968: "Oman (968)",
    92: "Pakistan (92)",
    680: "Palau (680)",
    970: "Palestine (970)",
    507: "Panama (507)",
    675: "Papua New Guinea (675)",
    595: "Paraguay (595)",
    51: "Peru (51)",
    63: "Philippines (63)",
    48: "Poland (48)",
    351: "Portugal (351)",
    1787: "Puerto Rico (1787)",
    974: "Qatar (974)",
    242: "Republic Of The Congo (242)",
    262: "Réunion Island (262)",
    40: "Romania (40)",
    7: "Russia (7)",
    250: "Rwanda (250)",
    1869: "Saint Kitts and Nevis (1869)",
    1758: "Saint Lucia (1758)",
    508: "Saint Pierre and Miquelon (508)",
    1784: "Saint Vincent and The Grenadines (1784)",
    685: "Samoa (685)",
    378: "San Marino (378)",
    239: "Sao Tome and Principe (239)",
    966: "Saudi Arabia (966)",
    221: "Senegal (221)",
    381: "Serbia (381)",
    248: "Seychelles (248)",
    232: "Sierra Leone (232)",
    65: "Singapore (65)",
    1721: "Sint Maarten(Dutch Part) (1721)",
    421: "Slovakia (421)",
    386: "Slovenia (386)",
    677: "Solomon Islands (677)",
    252: "Somalia (252)",
    27: "South Africa (27)",
    82: "South Korea (82)",
    34: "Spain (34)",
    94: "Sri Lanka (94)",
    249: "Sudan (249)",
    597: "Suriname (597)",
    268: "Swaziland (268)",
    46: "Sweden (46)",
    41: "Switzerland (41)",
    963: "Syria (963)",
    886: "Taiwan (886)",
    992: "Tajikistan (992)",
    255: "Tanzania (255)",
    66: "Thailand (66)",
    228: "Togo (228)",
    676: "Tonga (676)",
    1868: "Trinidad and Tobago (1868)",
    216: "Tunisia (216)",
    90: "Turkey (90)",
    993: "Turkmenistan (993)",
    1649: "Turks and Caicos Islands (1649)",
    256: "Uganda (256)",
    380: "Ukraine (380)",
    971: "United Arab Emirates (971)",
    44: "United Kingdom (44)",
    1: "United States (1)",
    598: "Uruguay (598)",
    998: "Uzbekistan (998)",
    678: "Vanuatu (678)",
    58: "Venezuela (58)",
    84: "Vietnam (84)",
    1340: "Virgin Islands,British (1340)",
    1284: "Virgin Islands,US (1284)",
    967: "Yemen (967)",
    260: "Zambia (260)",
    263: "Zimbabwe (263)",
}

# App names
APP_NAMES = {
    SUPER_SOCO: "Super Soco",
    VMOTO_SOCO: "Vmoto Soco",
}
