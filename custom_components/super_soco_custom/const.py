from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.const import (
    Platform,
    DEGREE,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TIMESTAMP,
    DEVICE_CLASS_VOLTAGE,
    LENGTH_KILOMETERS,
    LENGTH_METERS,
    PERCENTAGE,
    SPEED_KILOMETERS_PER_HOUR,
    TIME_SECONDS,
)

# Component
DOMAIN = "super_soco_custom"
NAME = "Super Soco Custom"
MANUFACTURER = "Super Soco"
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
    Platform.SWITCH,
]

# General
API_GEO_PRECISION = 4  # 4 decimals = 11.1 meters
CDN_BASE_URL = "https://oimg.supersocoeg.com:8996"
CONFIG_FLOW_VERSION = 1
COURSE_ROUNDING_ZEROES = 2
DISTANCE_ROUNDING_ZEROES = 2
HOME_ZONE = "zone.home"
KM_IN_A_M = 0.001
KMH_IN_A_MS = 3.6
LAST_TRIP_CACHE_SECONDS = 600
METERS_IN_EARTH_RADIUS = 6378160
POWER_ON_UPDATE_SECONDS = 10
SECONDS_IN_A_MINUTE = 60
SPEED_ROUNDING_ZEROES = 1
SPEED_THRESHOLD_KMH = 2

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
CONF_PASSWORD = "password"
CONF_PHONE_NUMBER = "phone_number"
CONF_PHONE_PREFIX = "phone_prefix"

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
DATA_ACCUMULATIVE_RIM = "accumulativeRim"
DATA_ADDRESS = "address"
DATA_AGREEMENT_END_TIME = "agreementEndTime"
DATA_AGREEMENT_START_TIME = "agreemenStartTime"  # Intended typo
DATA_ALTITUDE = "altitude"
DATA_BATTERY_PERCENTAGE = "nowElec"
DATA_CONTENT = "content"
DATA_COURSE = "course"
DATA_CREATE_TIME = "createTime"
DATA_DATA = "data"
DATA_DEVICE = "device"
DATA_DEVICE_NUMBER = "deviceNo"
DATA_DIR_OF_TRAVEL = "dir_of_travel"
DATA_DISPLAY_NAME = "display_name"
DATA_DISTANCE_FROM_HOME = "distance_from_home"
DATA_ELEVATION = "elevation"
DATA_ESTIMATED_RANGE = "endurance"
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
DATA_GPS_ACCURACY = "gps"
DATA_LAST_GPS_TIME = "lastGpsTime"
DATA_LAST_TRIP_BEGIN_LATITUDE = "beginLatitude"
DATA_LAST_TRIP_BEGIN_LONGITUDE = "beginLongitude"
DATA_LAST_TRIP_BEGIN_TIME = "beginTime"
DATA_LAST_TRIP_END_LATITUDE = "endLatitude"
DATA_LAST_TRIP_END_LONGITUDE = "endLongitude"
DATA_LAST_TRIP_END_TIME = "endTime"
DATA_LAST_TRIP_RIDE_DISTANCE = "rideDistance"
DATA_LAST_TRIP_RIDE_SPEED = "avgSpeed"
DATA_LAST_TRIP_RIDE_TIME = "rideTime"
DATA_LAST_WARNING_MESSAGE = "lastWarningMessage"
DATA_LAST_WARNING_TIME = "lastWarningTime"
DATA_LAST_WARNING_TITLE = "lastWarningTitle"
DATA_LATITUDE = "latitude"
DATA_LIST = "list"
DATA_LOCK = "lock"
DATA_LOGO_IMAGE_URL = "logoImg"
DATA_LONGITUDE = "longitude"
DATA_MODEL_NAME = "carModelName"
DATA_NATIVE_PUSH_NOTIFICATIONS = "isWarnPush"
DATA_NATIVE_TRACKING_HISTORY = "historyLocusSwitch"
DATA_POWER_STATUS = "powerStatus"
DATA_RADIUS = "radius"
DATA_RESULTS = "results"
DATA_REVERSE_GEOCODING = "reverse_geocoding"
DATA_SIGNAL_STRENGTH = "gsm"
DATA_SLEEP = "sleep"
DATA_SPEED = "speed"
DATA_TIMESTAMP = "timestamp"
DATA_TITLE = "title"
DATA_TRIP_DISTANCE = "mileages"
DATA_USER = "user"
DATA_VEHICLE_IMAGE_URL = "imgUrl"
DATA_VOLTAGE = "voltage"
DATA_WIND_ROSE_COURSE = "wind_rose_course"

# Error keys
ERROR_ALREADY_CONFIGURED = "already_configured"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_UNKNOWN = "unknown"

# Entities
BINARY_SENSORS = [
    (
        "power_status",  # Id
        "Power Status",  # Name
        DATA_POWER_STATUS,  # Data key
        1,  # Comparison condition
        "mdi:power-standby",  # Icon
        DEVICE_CLASS_POWER,  # Device class
        None,  # Extra attributes
    ),
]

DEVICE_TRACKERS = [
    (
        "location",  # Id
        "Location",  # Name
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
        "accumulative_rim",  # Id
        "Accumulative Rim",  # Name
        DATA_ACCUMULATIVE_RIM,  # Data key
        None,  # Unit of measurement
        "mdi:engine",  # Icon
        None,  # Device class
        None,  # Extra attributes
    ),
    (
        "agreement_start_time",
        "Agreement Start Time",
        DATA_AGREEMENT_START_TIME,
        None,
        "mdi:calendar-start",
        DEVICE_CLASS_TIMESTAMP,
        None,
    ),
    (
        "agreement_end_time",
        "Agreement End Time",
        DATA_AGREEMENT_END_TIME,
        None,
        "mdi:calendar-end",
        DEVICE_CLASS_TIMESTAMP,
        None,
    ),
    (
        "altitude",
        "Altitude",
        DATA_ALTITUDE,
        LENGTH_METERS,
        "mdi:elevation-rise",
        None,
        None,
    ),
    (
        "battery_percentage",
        "Battery Percentage",
        DATA_BATTERY_PERCENTAGE,
        PERCENTAGE,
        "mdi:battery",
        DEVICE_CLASS_BATTERY,
        None,
    ),
    (
        "course",
        "Course",
        DATA_COURSE,
        DEGREE,
        "mdi:compass",
        None,
        None,
    ),
    (
        "distance_from_home",
        "Distance From Home",
        DATA_DISTANCE_FROM_HOME,
        LENGTH_KILOMETERS,
        "mdi:home",
        None,
        {
            "dir_of_travel": DATA_DIR_OF_TRAVEL,
        },
    ),
    (
        "estimated_range",
        "Estimated Range",
        DATA_ESTIMATED_RANGE,
        LENGTH_KILOMETERS,
        "mdi:map-marker-path",
        None,
        None,
    ),
    (
        "reverse_geocoding",
        "Reverse Geocoding",
        DATA_REVERSE_GEOCODING,
        None,
        "mdi:map",
        None,
        {
            "city": DATA_REVERSE_GEOCODING_CITY,
            "country": DATA_REVERSE_GEOCODING_COUNTRY,
            "country_code": DATA_REVERSE_GEOCODING_COUNTRY_CODE,
            "county": DATA_REVERSE_GEOCODING_COUNTY,
            "house_number": DATA_REVERSE_GEOCODING_HOUSE_NUMBER,
            "neighbourhood": DATA_REVERSE_GEOCODING_NEIGHBOURHOOD,
            "postcode": DATA_REVERSE_GEOCODING_POSTCODE,
            "road": DATA_REVERSE_GEOCODING_ROAD,
            "state": DATA_REVERSE_GEOCODING_STATE,
            "state_district": DATA_REVERSE_GEOCODING_STATE_DISTRICT,
        },
    ),
    (
        "gps_accuracy",
        "GPS Accuracy",
        DATA_GPS_ACCURACY,
        None,
        "mdi:crosshairs-gps",
        None,
        None,
    ),
    (
        "image",
        "Image",
        DATA_VEHICLE_IMAGE_URL,
        None,
        "mdi:image",
        None,
        None,
    ),
    (
        "last_gps_time",
        "Last GPS Time",
        DATA_LAST_GPS_TIME,
        None,
        "mdi:web-clock",
        DEVICE_CLASS_TIMESTAMP,
        None,
    ),
    (
        "last_trip_average_speed",
        "Last Trip Average Speed",
        DATA_LAST_TRIP_RIDE_SPEED,
        SPEED_KILOMETERS_PER_HOUR,
        "mdi:speedometer",
        None,
        None,
    ),
    (
        "last_trip_distance",
        "Last Trip Distance",
        DATA_LAST_TRIP_RIDE_DISTANCE,
        LENGTH_KILOMETERS,
        "mdi:map-marker-distance",
        None,
        {
            "begin_latitude": DATA_LAST_TRIP_BEGIN_LATITUDE,
            "begin_longitude": DATA_LAST_TRIP_BEGIN_LONGITUDE,
            "end_latitude": DATA_LAST_TRIP_END_LATITUDE,
            "end_longitude": DATA_LAST_TRIP_END_LONGITUDE,
        },
    ),
    (
        "last_trip_duration",
        "Last Trip Duration",
        DATA_LAST_TRIP_RIDE_TIME,
        TIME_SECONDS,
        "mdi:timer",
        None,
        {
            "begin_time": DATA_LAST_TRIP_BEGIN_TIME,
            "end_time": DATA_LAST_TRIP_END_TIME,
        },
    ),
    (
        "last_warning",
        "Last Warning",
        DATA_LAST_WARNING_TIME,
        None,
        "mdi:alert-circle",
        DEVICE_CLASS_TIMESTAMP,
        {
            "title": DATA_LAST_WARNING_TITLE,
            "message": DATA_LAST_WARNING_MESSAGE,
        },
    ),
    (
        "lock",
        "Lock",
        DATA_LOCK,
        None,
        "mdi:lock",
        None,
        None,
    ),
    (
        "logo",
        "Logo",
        DATA_LOGO_IMAGE_URL,
        None,
        "mdi:image",
        None,
        None,
    ),
    (
        "signal_strength",
        "Signal Strength",
        DATA_SIGNAL_STRENGTH,
        None,
        "mdi:signal",
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
    ),
    (
        "sleep",
        "Sleep",
        DATA_SLEEP,
        None,
        "mdi:sleep",
        None,
        None,
    ),
    (
        "speed",
        "Speed",
        DATA_SPEED,
        SPEED_KILOMETERS_PER_HOUR,
        "mdi:speedometer",
        None,
        None,
    ),
    (
        "trip_distance",
        "Trip Distance",
        DATA_TRIP_DISTANCE,
        LENGTH_KILOMETERS,
        "mdi:map-marker-distance",
        None,
        None,
    ),
    (
        "voltage",
        "Voltage",
        DATA_VOLTAGE,
        None,
        "mdi:current-dc",
        DEVICE_CLASS_VOLTAGE,
        None,
    ),
    (
        "wind_rose_course",
        "Wind Rose Course",
        DATA_WIND_ROSE_COURSE,
        None,
        "mdi:compass-rose",
        None,
        None,
    ),
]

SWITCHES = [
    (
        "native_push_notifications",  # Id
        "Native Push Notifications",  # Name
        DATA_NATIVE_PUSH_NOTIFICATIONS,  # Data key
        1,  # Comparison condition
        "mdi:bell-ring",  # Icon
        None,  # Extra attributes
    ),
    (
        "native_tracking_history",
        "Native Tracking History",
        DATA_NATIVE_TRACKING_HISTORY,
        1,
        "mdi:database-marker",
        None,
    ),
]

# Switch API methods
SWITCH_API_METHODS = {
    DATA_NATIVE_PUSH_NOTIFICATIONS: "set_push_notifications",
    DATA_NATIVE_TRACKING_HISTORY: "set_tracking_history",
}

# Phone prefixes
PHONE_PREFIXES = {
    93: "Afghanistan (93)",
    355: "Albania (355)",
    244: "Angola (244)",
    376: "Andorra (376)",
    971: "United Arab Emirates (971)",
    1268: "Antigua and Barbuda (1268)",
    1264: "Anguilla (1264)",
    374: "Armenia (374)",
    54: "Argentina (54)",
    1684: "American Samoa (1684)",
    43: "Austria (43)",
    61: "Australia (61)",
    297: "Aruba (297)",
    994: "Azerbaijan (994)",
    387: "Bosnia and Herzegovina (387)",
    1246: "Barbados (1246)",
    880: "Bangladesh (880)",
    32: "Belgium (32)",
    226: "Burkina Faso (226)",
    359: "Bulgaria (359)",
    973: "Bahrain (973)",
    257: "Burundi (257)",
    229: "Benin (229)",
    970: "Palestine (970)",
    1441: "Bermuda (1441)",
    673: "Brunei (673)",
    591: "Bolivia (591)",
    55: "Brazil (55)",
    1242: "Bahamas (1242)",
    975: "Bhutan (975)",
    267: "Botswana (267)",
    375: "Belarus (375)",
    501: "Belize (501)",
    1: "Canada (1)",
    243: "Democratic Republic of the Congo (243)",
    236: "Central African Republic (236)",
    242: "Republic Of The Congo (242)",
    41: "Switzerland (41)",
    86: "China (86)",
    225: "Ivory Coast (225)",
    682: "Cook Islands (682)",
    56: "Chile (56)",
    237: "Cameroon (237)",
    57: "Colombia (57)",
    506: "Costa Rica (506)",
    53: "Cuba (53)",
    238: "Cape Verde (238)",
    599: "Curacao (599)",
    357: "Cyprus (357)",
    420: "Czech (420)",
    49: "Germany (49)",
    253: "Djibouti (253)",
    45: "Denmark (45)",
    1767: "Dominica (1767)",
    1809: "Dominican Republic (1809)",
    213: "Algeria (213)",
    593: "Ecuador (593)",
    372: "Estonia (372)",
    20: "Egypt (20)",
    291: "Eritrea (291)",
    34: "Spain (34)",
    251: "Ethiopia (251)",
    358: "Finland (358)",
    679: "Fiji (679)",
    298: "Faroe Islands (298)",
    33: "France (33)",
    241: "Gabon (241)",
    44: "United Kingdom (44)",
    1473: "Grenada (1473)",
    995: "Georgia (995)",
    594: "French Guiana (594)",
    233: "Ghana (233)",
    350: "Gibraltar (350)",
    299: "Greenland (299)",
    220: "Gambia (220)",
    224: "Guinea (224)",
    590: "Guadeloupe (590)",
    240: "Equatorial Guinea (240)",
    30: "Greece (30)",
    502: "Guatemala (502)",
    1671: "Guam (1671)",
    245: "Guinea-Bissau (245)",
    592: "Guyana (592)",
    852: "Hong Kong (852)",
    504: "Honduras (504)",
    385: "Croatia (385)",
    509: "Haiti (509)",
    36: "Hungary (36)",
    62: "Indonesia (62)",
    353: "Ireland (353)",
    972: "Israel (972)",
    91: "India (91)",
    964: "Iraq (964)",
    98: "Iran (98)",
    354: "Iceland (354)",
    39: "Italy (39)",
    1876: "Jamaica (1876)",
    962: "Jordan (962)",
    81: "Japan (81)",
    254: "Kenya (254)",
    996: "Kyrgyzstan (996)",
    855: "Cambodia (855)",
    686: "Kiribati (686)",
    269: "Comoros (269)",
    1869: "Saint Kitts and Nevis (1869)",
    82: "South Korea (82)",
    965: "Kuwait (965)",
    1345: "Cayman Islands (1345)",
    7: "Kazakhstan (7)",
    856: "Laos (856)",
    961: "Lebanon (961)",
    1758: "Saint Lucia (1758)",
    423: "Liechtenstein (423)",
    94: "Sri Lanka (94)",
    231: "Liberia (231)",
    266: "Lesotho (266)",
    370: "Lithuania (370)",
    352: "Luxembourg (352)",
    371: "Latvia (371)",
    218: "Libya (218)",
    212: "Morocco (212)",
    377: "Monaco (377)",
    373: "Moldova (373)",
    382: "Montenegro (382)",
    261: "Madagascar (261)",
    389: "Macedonia (389)",
    223: "Mali (223)",
    95: "Myanmar (95)",
    976: "Mongolia (976)",
    853: "Macau (853)",
    596: "Martinique (596)",
    222: "Mauritania (222)",
    1664: "Montserrat (1664)",
    356: "Malta (356)",
    230: "Mauritius (230)",
    960: "Maldives (960)",
    265: "Malawi (265)",
    52: "Mexico (52)",
    60: "Malaysia (60)",
    258: "Mozambique (258)",
    264: "Namibia (264)",
    687: "New Caledonia (687)",
    227: "Niger (227)",
    234: "Nigeria (234)",
    505: "Nicaragua (505)",
    31: "Netherlands (31)",
    47: "Norway (47)",
    977: "Nepal (977)",
    64: "New Zealand (64)",
    968: "Oman (968)",
    507: "Panama (507)",
    51: "Peru (51)",
    689: "French Polynesia (689)",
    675: "Papua New Guinea (675)",
    63: "Philippines (63)",
    92: "Pakistan (92)",
    48: "Poland (48)",
    508: "Saint Pierre and Miquelon (508)",
    1787: "Puerto Rico (1787)",
    351: "Portugal (351)",
    680: "Palau (680)",
    595: "Paraguay (595)",
    974: "Qatar (974)",
    262: "Réunion Island (262)",
    40: "Romania (40)",
    381: "Serbia (381)",
    7: "Russia (7)",
    250: "Rwanda (250)",
    966: "Saudi Arabia (966)",
    677: "Solomon Islands (677)",
    248: "Seychelles (248)",
    249: "Sudan (249)",
    46: "Sweden (46)",
    65: "Singapore (65)",
    386: "Slovenia (386)",
    421: "Slovakia (421)",
    232: "Sierra Leone (232)",
    378: "San Marino (378)",
    221: "Senegal (221)",
    252: "Somalia (252)",
    597: "Suriname (597)",
    239: "Sao Tome and Principe (239)",
    503: "El Salvador (503)",
    1721: "Sint Maarten(Dutch Part) (1721)",
    963: "Syria (963)",
    268: "Swaziland (268)",
    1649: "Turks and Caicos Islands (1649)",
    235: "Chad (235)",
    228: "Togo (228)",
    66: "Thailand (66)",
    992: "Tajikistan (992)",
    670: "East Timor (670)",
    993: "Turkmenistan (993)",
    216: "Tunisia (216)",
    676: "Tonga (676)",
    90: "Turkey (90)",
    1868: "Trinidad and Tobago (1868)",
    886: "Taiwan (886)",
    255: "Tanzania (255)",
    380: "Ukraine (380)",
    256: "Uganda (256)",
    1: "United States (1)",
    598: "Uruguay (598)",
    998: "Uzbekistan (998)",
    1784: "Saint Vincent and The Grenadines (1784)",
    58: "Venezuela (58)",
    1340: "Virgin Islands,British (1340)",
    1284: "Virgin Islands,US (1284)",
    84: "Vietnam (84)",
    678: "Vanuatu (678)",
    685: "Samoa (685)",
    967: "Yemen (967)",
    269: "Mayotte (269)",
    27: "South Africa (27)",
    260: "Zambia (260)",
    263: "Zimbabwe (263)",
}
