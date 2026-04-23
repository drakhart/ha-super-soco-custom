import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.core_config import Config
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_EMAIL,
    CONF_LOGIN_METHOD,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
    CONF_TOKEN,
    DOMAIN,
    LOGIN_METHOD_PHONE,
    NAME,
    OPT_EMAIL,
    PLATFORMS,
)
from .coordinator import VmotoDataUpdateCoordinator
from .open_street_map_api import OpenStreetMapAPI
from .open_topo_data_api import OpenTopoDataAPI
from .vmoto_api import VmotoAPI

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = config_validation.config_entry_only_config_schema(DOMAIN)


async def async_setup(
    hass: HomeAssistant,
    config: Config,
) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    phone_prefix_raw = config_entry.data.get(CONF_PHONE_PREFIX)
    phone_prefix: int | None = (
        int(phone_prefix_raw) if phone_prefix_raw is not None else None
    )
    phone_number: str | None = config_entry.data.get(CONF_PHONE_NUMBER)
    token: str | None = config_entry.data.get(CONF_TOKEN)
    conf_email: str | None = config_entry.data.get(CONF_EMAIL)
    opt_email: str | None = config_entry.options.get(OPT_EMAIL)

    session = async_get_clientsession(hass)
    client = VmotoAPI(
        session,
        phone_prefix=phone_prefix,
        phone_number=phone_number,
        email=conf_email,
        token=token,
    )

    open_street_map_api = OpenStreetMapAPI(session, opt_email)
    open_topo_data_api = OpenTopoDataAPI(session)
    coordinator = VmotoDataUpdateCoordinator(
        hass,
        config_entry,
        client,
        open_street_map_api,
        open_topo_data_api,
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    _LOGGER.info("Added new %s device with entry_id: %s", NAME, config_entry.entry_id)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloaded %s device with entry_id: %s", NAME, config_entry.entry_id)

    unloaded = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    if unloaded:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    await async_unload_entry(hass, config_entry)
    await async_setup_entry(hass, config_entry)

    _LOGGER.info("Reloaded %s device with entry_id: %s", NAME, config_entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        new[CONF_TOKEN] = None

        hass.config_entries.async_update_entry(config_entry, data=new, version=2)

    if config_entry.version == 2:
        new = {**config_entry.data}

        if new.get(CONF_EMAIL) is None:
            new[CONF_LOGIN_METHOD] = LOGIN_METHOD_PHONE

        hass.config_entries.async_update_entry(config_entry, data=new, version=3)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True
