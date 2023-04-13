"""Constants for super_soco_custom tests."""
from custom_components.super_soco_custom.const import (
    CONF_APP_NAME,
    CONF_LOGIN_CODE,
    CONF_PASSWORD,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    CONF_TOKEN,
    OPT_EMAIL,
    SUPER_SOCO,
    VMOTO_SOCO,
)

# Mock config data to be used across multiple tests
MOCK_DEVICE_NO = "1234567890123456"
MOCK_OPTIONS = {
    OPT_EMAIL: "test@test.com",
}
MOCK_SUPER_SOCO_CONFIG = {
    CONF_APP_NAME: SUPER_SOCO,
    CONF_LOGIN_CODE: None,
    CONF_PASSWORD: "test",
    CONF_PHONE_NUMBER: "123456789",
    CONF_PHONE_PREFIX: 34,
    CONF_TOKEN: None,
}
MOCK_USER_ID = "1234"
MOCK_VMOTO_SOCO_CONFIG = {
    CONF_APP_NAME: VMOTO_SOCO,
    CONF_LOGIN_CODE: "1234",
    CONF_PASSWORD: None,
    CONF_PHONE_NUMBER: "123456789",
    CONF_PHONE_PREFIX: 34,
    CONF_TOKEN: None,
}
