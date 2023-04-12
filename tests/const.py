"""Constants for super_soco_custom tests."""
from custom_components.super_soco_custom.const import (
    CONF_APP_NAME,
    CONF_LOGIN_CODE,
    CONF_PHONE_PREFIX,
    CONF_PHONE_NUMBER,
    CONF_PASSWORD,
    CONF_TOKEN,
    OPT_EMAIL,
    SUPER_SOCO,
)

# Mock config data to be used across multiple tests
MOCK_CONFIG_SUPER_SOCO = {
    CONF_APP_NAME: SUPER_SOCO,
    CONF_LOGIN_CODE: None,
    CONF_PHONE_NUMBER: "123456789",
    CONF_PHONE_PREFIX: 34,
    CONF_PASSWORD: "test",
    CONF_TOKEN: None,
}

MOCK_OPTIONS = {
    OPT_EMAIL: "test@test.com",
}
