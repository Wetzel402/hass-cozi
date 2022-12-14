"""Cozi integration for HA."""
from __future__ import annotations

from datetime import timedelta
import logging

from cozi import Cozi
from cozi.exceptions import CoziException
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import DOMAIN, LOGGER, UPDATE_INTERVAL, VERSION
from .coordinator import CoziCoordinator
from .utilities import Utilities

entryTitle = ""

PLATFORMS = [Platform.SENSOR]

SERVICE_ADD_LIST = "add_list"
SERVICE_REMOVE_LIST = "remove_list"
SERVICE_ADD_ITEM = "add_item"
SERVICE_EDIT_ITEM = "edit_item"
SERVICE_MARK_ITEM = "mark_item"
SERVICE_REMOVE_ITEMS = "remove_items"
SERVICE_REORDER_ITEMS = "reorder_items"
SERVICE_REFRESH = "refresh"

ATTR_LIST_TITLE = "list_title"
ATTR_LIST_TYPE = "list_type"
ATTR_LIST_ID = "list_id"
ATTR_ITEM_TEXT = "item_text"
ATTR_ITEM_POS = "item_pos"
ATTR_ITEM_ID = "item_id"
ATTR_STATUS = "status"
ATTR_ITEM_IDS = "item_ids"
ATTR_ITEMS_LIST = "items_list"

class CoziInit:
    def __init__(self, _cozi: Cozi) -> None:
        """Initialize."""
        self.cozi = _cozi


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration using UI"""
    LOGGER.debug("Setting up Cozi integration...")

    user_name: str = entry.data[CONF_USERNAME]
    password: str = entry.data[CONF_PASSWORD]
    assert entry.unique_id is not None

    """create instance of cozi"""
    user_name: str = hass.config_entries.async_entries(DOMAIN)[0].data[CONF_USERNAME]
    password: str = hass.config_entries.async_entries(DOMAIN)[0].data[CONF_PASSWORD]
    cozi = Cozi(user_name, password)
    cozi_init = CoziInit(cozi)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = cozi_init
    hass.data[DOMAIN]["init"] = cozi_init

    entryTitle = entry.title

    coordinator = CoziCoordinator(
        hass, LOGGER, name=entryTitle, update_interval=UPDATE_INTERVAL
    )
    coordinator.async_set_updated_data(None)
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.data[DOMAIN]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))
    # await add_services(hass)
    await add_event_handlers(hass)
    if hass.is_running:
        # integration reloaded or options changed via UI
        await coordinator.async_config_entry_first_refresh()
    else:
        # first run, home assistant is loading
        LOGGER.info("Cozi version [%s] started.", VERSION)
        await coordinator.async_refresh()

    await hass.async_add_executor_job(setup_hass_services, hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, SERVICE_ADD_LIST)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)


async def add_event_handlers(hass: HomeAssistant):
    """add event handlers"""
    coordinator = hass.data[DOMAIN]["coordinator"]

    async def async_schedule_refresh_states(hass, delay):
        """schedule refresh of the sensors state"""
        now = dt_util.utcnow()
        next_interval = now + timedelta(seconds=delay)
        async_track_point_in_utc_time(hass, async_delayed_refresh_states, next_interval)

    async def async_delayed_refresh_states(timedate):
        """refresh sensors state"""
        await coordinator.async_refresh()

    async def async_on_home_assistant_started(event):
        startup_delay = get_config(hass, "startup_delay", 0)
        await async_schedule_refresh_states(hass, startup_delay)

    async def async_on_configuration_changed(event):
        typ = event.event_type
        if typ == EVENT_CALL_SERVICE:
            domain = event.data.get("domain", None)
            service = event.data.get("service", None)
            if domain in TRACKED_EVENT_DOMAINS and service in [
                "reload_core_config",
                "reload",
            ]:
                await coordinator.async_refresh()

        elif typ in [EVENT_AUTOMATION_RELOADED, EVENT_SCENE_RELOADED]:
            await coordinator.async_refresh()


def setup_hass_services(hass: HomeAssistant) -> None:
    """Home Assistant services."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    util = Utilities()

    async def add_list(call: ServiceCall) -> None:
        """Add a list."""
        list_title = call.data[ATTR_LIST_TITLE]
        list_type = call.data[ATTR_LIST_TYPE]

        try:
            LOGGER.debug(
                "add_list service called with list_title: {} and list_type: {}".format(
                    list_title, list_type
                )
            )
            await hass.data[DOMAIN]["init"].cozi.add_list(list_title, list_type)
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    async def remove_list(call: ServiceCall) -> None:
        """Remove a list."""
        list_id = call.data[ATTR_LIST_ID]

        try:
            LOGGER.debug("remove_list service called with list_id: {}".format(list_id))
            await hass.data[DOMAIN]["init"].cozi.remove_list(list_id)
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    async def add_item(call: ServiceCall) -> None:
        """Adds an item to a list."""
        list_id = call.data[ATTR_LIST_ID]
        item_text = call.data[ATTR_ITEM_TEXT]
        item_pos = call.data[ATTR_ITEM_POS]

        try:
            LOGGER.debug(
                "add_item service called with list_id: {} , item_text: {} , and item_pos: {}".format(
                    list_id, item_text, item_pos
                )
            )
            await util.local_add_item(hass, list_id, item_text, item_pos)
            await hass.data[DOMAIN]["init"].cozi.add_item(list_id, item_text, item_pos)
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    async def edit_item(call: ServiceCall) -> None:
        """Edits an item in a list."""
        list_id = call.data[ATTR_LIST_ID]
        item_id = call.data[ATTR_ITEM_ID]
        item_text = call.data[ATTR_ITEM_TEXT]

        try:
            LOGGER.debug(
                "edit_item service called with list_id: {} , item_id: {} , and item_text: {}".format(
                    list_id, item_id, item_text
                )
            )
            await util.local_edit_item(hass, list_id, item_id, item_text)
            await hass.data[DOMAIN]["init"].cozi.edit_item(list_id, item_id, item_text)
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    async def mark_item(call: ServiceCall) -> None:
        """Marks or checks off an item in a list."""
        list_id = call.data[ATTR_LIST_ID]
        item_id = call.data[ATTR_ITEM_ID]
        status = call.data[ATTR_STATUS]

        try:
            LOGGER.debug(
                "mark_item service called with list_id: {} , item_id: {} , and status: {}".format(
                    list_id, item_id, status
                )
            )
            await util.local_mark_item(hass, list_id, item_id, status)
            await hass.data[DOMAIN]["init"].cozi.mark_item(list_id, item_id, status)
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    async def remove_items(call: ServiceCall) -> None:
        """Removes items from a list."""
        list_id = call.data[ATTR_LIST_ID]
        item_ids = call.data[ATTR_ITEM_IDS]

        try:
            LOGGER.debug(
                "remove_item service called with list_id: {} and item_ids: {}".format(
                    list_id, item_ids
                )
            )
            await util.local_remove_items(hass, list_id, item_ids)
            await hass.data[DOMAIN]["init"].cozi.remove_items(list_id, item_ids)
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    async def reorder_items(call: ServiceCall) -> None:
        """Reorders items in a list."""
        list_id = call.data[ATTR_LIST_ID]
        list_title = call.data[ATTR_LIST_TITLE]
        items_list = call.data[ATTR_ITEMS_LIST]
        list_type = call.data[ATTR_LIST_TYPE]

        try:
            LOGGER.debug(
                "reorder_items service called with list_id: {}, list_title: {}, items_list: {}, and list_type: {}".format(
                    list_id, list_title, items_list, list_type
                )
            )
            await util.local_reorder_list(hass, list_id, items_list)
            await hass.data[DOMAIN]["init"].cozi.reorder_list(list_id, list_title, items_list, list_type)
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    async def refresh(call: ServiceCall) -> None:
        """Refresh Cozi entities."""

        try:
            LOGGER.debug(
                "refresh service called"
                )
            await coordinator.async_refresh()
        except CoziException as ex:
            LOGGER.warning(ex)

    hass.services.register(
        DOMAIN,
        SERVICE_ADD_LIST,
        add_list,
        schema=vol.Schema(
            {
                vol.Required(ATTR_LIST_TITLE): cv.string,
                vol.Required(ATTR_LIST_TYPE): cv.string,
            }
        ),
    )

    hass.services.register(
        DOMAIN,
        SERVICE_REMOVE_LIST,
        remove_list,
        schema=vol.Schema({vol.Required(ATTR_LIST_ID): cv.string}),
    )

    # TODO enum
    hass.services.register(
        DOMAIN,
        SERVICE_ADD_ITEM,
        add_item,
        schema=vol.Schema(
            {
                vol.Required(ATTR_LIST_ID): cv.string,
                vol.Required(ATTR_ITEM_TEXT): cv.string,
                vol.Required(ATTR_ITEM_POS): int,
            }
        ),
    )

    hass.services.register(
        DOMAIN,
        SERVICE_EDIT_ITEM,
        edit_item,
        schema=vol.Schema(
            {
                vol.Required(ATTR_LIST_ID): cv.string,
                vol.Required(ATTR_ITEM_ID): cv.string,
                vol.Required(ATTR_ITEM_TEXT): cv.string,
            }
        ),
    )

    hass.services.register(
        DOMAIN,
        SERVICE_MARK_ITEM,
        mark_item,
        schema=vol.Schema(
            {
                vol.Required(ATTR_LIST_ID): cv.string,
                vol.Required(ATTR_ITEM_ID): cv.string,
                vol.Required(ATTR_STATUS): cv.string,
            }
        ),
    )

    hass.services.register(
        DOMAIN,
        SERVICE_REMOVE_ITEMS,
        remove_items,
        schema=vol.Schema(
            {
                vol.Required(ATTR_LIST_ID): cv.string,
                vol.Required(ATTR_ITEM_IDS): cv.ensure_list,
            }
        ),
    )

    hass.services.register(
        DOMAIN,
        SERVICE_REORDER_ITEMS,
        reorder_items,
        schema=vol.Schema(
            {
                vol.Required(ATTR_LIST_ID): cv.string,
                vol.Required(ATTR_LIST_TITLE): cv.string,
                vol.Required(ATTR_ITEMS_LIST): cv.ensure_list,
                vol.Required(ATTR_LIST_TYPE): cv.string,
            }
        ),
    )

    hass.services.register(
        DOMAIN,
        SERVICE_REFRESH,
        refresh,
    )