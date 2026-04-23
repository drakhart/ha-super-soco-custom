"""Constants for vmoto tests."""

from custom_components.super_soco_custom.const import (
    CONF_LOGIN_CODE,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    CONF_TOKEN,
    OPT_EMAIL,
)

# Mock config data to be used across multiple tests
MOCK_DEVICE_NO = "1234567890123456"
MOCK_OPTIONS = {
    OPT_EMAIL: "test@test.com",
}
MOCK_USER_ID = 1234
MOCK_VMOTO_CONFIG = {
    CONF_LOGIN_CODE: "1234",
    CONF_PHONE_NUMBER: "123456789",
    CONF_PHONE_PREFIX: "34",
    CONF_TOKEN: None,
}
