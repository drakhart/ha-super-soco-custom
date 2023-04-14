"""Tests for super_soco_custom open_topo_data_api."""
import datetime
import pytz

from custom_components.super_soco_custom.helpers import (
    calculate_course,
    parse_timestamp,
)


def test_calculate_course():
    """Test calculate_course."""
    assert calculate_course(1, 1, 2, 2) == 44.98
    assert calculate_course(1, 0, 1, 0) == 0
    assert calculate_course(1, 1, -1, -1) == 225.0


def test_parse_timestamp():
    """Test parse_timestamp."""
    assert parse_timestamp(1681423654000) == datetime.datetime(
        2023, 4, 14, 6, 7, 34, tzinfo=pytz.UTC
    )
