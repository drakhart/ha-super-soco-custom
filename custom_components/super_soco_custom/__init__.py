from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .super_soco_api import SuperSocoAPI
from .open_street_map_api import OpenStreetMapAPI
from .open_topo_data_api import OpenTopoDataAPI
from .const import (
    DOMAIN,
    OPT_EMAIL,
    PLATFORMS,
    CONF_PASSWORD,
    CONF_PHONE_NUMBER,
    CONF_PHONE_PREFIX,
)
from .coordinator import SuperSocoCustomDataUpdateCoordinator


async def async_setup(hass: HomeAssistant, config: Config):
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    email = config_entry.data.get(OPT_EMAIL)
    phone_prefix = config_entry.data.get(CONF_PHONE_PREFIX)
    phone_number = config_entry.data.get(CONF_PHONE_NUMBER)
    password = config_entry.data.get(CONF_PASSWORD)

    session = async_get_clientsession(hass)
    super_soco_api = SuperSocoAPI(session, phone_prefix, phone_number, password)
    open_street_map_api = OpenStreetMapAPI(session, email)
    open_topo_data_api = OpenTopoDataAPI(session)
    coordinator = SuperSocoCustomDataUpdateCoordinator(
        hass,
        config_entry,
        super_soco_api,
        open_street_map_api,
        open_topo_data_api,
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    if unloaded:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
