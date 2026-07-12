"""Tests for vmoto helpers."""

from datetime import datetime

import pytz

from custom_components.super_soco_custom.helpers import (
    calculate_course,
    parse_date,
    parse_timestamp,
)


def test_calculate_course():
    """Test calculate_course."""
    assert calculate_course(1, 1, 2, 2) == 44.98
    assert calculate_course(1, 0, 1, 0) == 0
    assert calculate_course(1, 1, -1, -1) == 225.0


def test_parse_timestamp():
    """Test parse_timestamp."""
    assert parse_timestamp(1681423654000) == datetime(
        2023, 4, 13, 22, 7, 34, tzinfo=pytz.UTC
    )


def test_parse_date():
    """Test parse_date converts AM/PM date strings to datetime."""
    result = parse_date("13/04/2023 22:07AM")
    assert result.year == 2023
    assert result.month == 4
    assert result.day == 13
    assert result.hour == 22
    assert result.minute == 7
