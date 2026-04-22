import re
import pytz

from datetime import datetime
from math import acos, cos, sin, radians
from numpy import arctan2, degrees

from .const import (
    COURSE_ROUNDING_DECIMALS,
    DEFAULT_FLOAT,
    METERS_IN_EARTH_RADIUS,
    MILLISECONDS_IN_A_SECOND,
)


def calculate_course(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    if lat1 == lat2 and lon1 == lon2:
        return DEFAULT_FLOAT

    dLon = lon2 - lon1

    x = cos(radians(lat2)) * sin(radians(dLon))
    y = cos(radians(lat1)) * sin(radians(lat2)) - sin(radians(lat1)) * cos(
        radians(lat2)
    ) * cos(radians(dLon))

    course = degrees(arctan2(x, y))

    if course < 0:
        course = 360 + course

    return round(course, COURSE_ROUNDING_DECIMALS)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    if lat1 == lat2 and lon1 == lon2:
        return DEFAULT_FLOAT

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    rho1 = METERS_IN_EARTH_RADIUS * cos(lat1)
    z1 = METERS_IN_EARTH_RADIUS * sin(lat1)
    x1 = rho1 * cos(lon1)
    y1 = rho1 * sin(lon1)

    rho2 = METERS_IN_EARTH_RADIUS * cos(lat2)
    z2 = METERS_IN_EARTH_RADIUS * sin(lat2)
    x2 = rho2 * cos(lon2)
    y2 = rho2 * sin(lon2)

    dot = x1 * x2 + y1 * y2 + z1 * z2
    cos_theta = dot / (METERS_IN_EARTH_RADIUS * METERS_IN_EARTH_RADIUS)
    theta = acos(cos_theta)

    return METERS_IN_EARTH_RADIUS * theta


def calculate_percentage(current: float, maximum: float, decimals: int = 0) -> float:
    return min(round(100 * (current / maximum), decimals), 100)


def calculate_wind_rose_course(course: float) -> str:
    wind_rose_brackets = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]

    return wind_rose_brackets[round(course / 45)]


def parse_date(date_string: str) -> datetime:
    clean_string = re.sub("AM|PM", "+01:00", date_string)
    return datetime.strptime(clean_string, "%d/%m/%Y %H:%M%z")


def parse_timestamp(timestampMilliseconds: int) -> datetime:
    timestamp = timestampMilliseconds / MILLISECONDS_IN_A_SECOND

    return datetime.fromtimestamp(timestamp, tz=pytz.UTC)
