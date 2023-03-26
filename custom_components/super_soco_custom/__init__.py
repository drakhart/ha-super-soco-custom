import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .super_soco_api import SuperSocoAPI
from .open_street_map_api import OpenStreetMapAPI
from .open_topo_data_api import OpenTopoDataAPI
from .const import (
    CONF_CLIENT,
    CONF_SESSION,
    CONFIG_FLOW_VERSION,
    DOMAIN,
    NAME,
    OPT_EMAIL,
    PLATFORMS,
)
from .coordinator import SuperSocoCustomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(
    hass: HomeAssistant, config: Config  # pylint: disable=unused-argument
) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    email = config_entry.data.get(OPT_EMAIL)
    session = config_entry.data.get(CONF_SESSION)
    open_street_map_api = OpenStreetMapAPI(session, email)
    open_topo_data_api = OpenTopoDataAPI(session)
    coordinator = SuperSocoCustomDataUpdateCoordinator(
        hass,
        config_entry,
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


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: ConfigEntry  # pylint: disable=unused-argument
) -> bool:
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating %s device from version %s to version %s",
        NAME,
        config_entry.version,
        CONFIG_FLOW_VERSION,
    )
    _LOGGER.info("Migration not required")

    return True
