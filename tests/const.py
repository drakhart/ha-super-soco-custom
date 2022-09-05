"""Constants for super_soco_custom tests."""
from custom_components.super_soco_custom.const import (
    CONF_PHONE_PREFIX,
    CONF_PHONE_NUMBER,
    CONF_PASSWORD,
    OPT_EMAIL,
)

# Mock config data to be used across multiple tests
MOCK_CONFIG = {
    CONF_PHONE_PREFIX: 34,
    CONF_PHONE_NUMBER: "123456789",
    CONF_PASSWORD: "test",
}

MOCK_OPTIONS = {
    OPT_EMAIL: "test@test.com",
}
