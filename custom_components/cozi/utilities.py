from __future__ import annotations

import logging

from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant as hass
from .const import DOMAIN, LOGGER

"""Updates the entity locally so we don't have to"""
"""wait for the reply from Cozi for a UI update"""

class Utilities():
    def __init__(self):
        """Initialize."""
        self.data = {
            "last_update": dt_util.now(),
            "unit_of_measurement": "list",
            "icon": "mdi:format-list-bulleted-square",
            "friendly_name": "cozi_lists",
        }

    async def local_add_item(
        self, 
        hass: HomeAssistant, 
        list_id: str, 
        item_text: str,
        item_pos: int
        ) -> None:
        try:
            lists = hass.data[DOMAIN]["lists"]
            for iList, item in enumerate(lists):
                if item["listId"] == list_id:
                    lists[iList]["items"].insert(item_pos, {
                        "status": "incomplete",
                        "itemId": None,
                        "itemType": None,
                        "text": item_text
                        })
                    self.data["lists"] = lists
                    "HA doesn't think the list changed so set it to none first..."
                    hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", None)
                    hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", self.data)
                    break
        except KeyError as ex:
            LOGGER.warning(ex)

    async def local_edit_item(
        self, 
        hass: HomeAssistant, 
        list_id: str, 
        item_id: str, 
        item_text: str
        ) -> None:
        try:
            lists = hass.data[DOMAIN]["lists"]
            for iList, item in enumerate(lists):
                if item["listId"] == list_id:
                    for iItem, item in enumerate(item["items"]):
                        if item["itemId"] == item_id:
                            lists[iList]["items"][iItem]["text"] = item_text
                            self.data["lists"] = lists
                            "HA doesn't think the list changed so set it to none first..."
                            hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", None)
                            hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", self.data)
                            break
                            break
        except KeyError as ex:
            LOGGER.warning(ex)

    async def local_mark_item(
        self, 
        hass: HomeAssistant, 
        list_id: str, 
        item_id: str, 
        status: str
        ) -> None:
        try:
            lists = hass.data[DOMAIN]["lists"]
            for iList, item in enumerate(lists):
                if item["listId"] == list_id:
                    for iItem, item in enumerate(item["items"]):
                        if item["itemId"] == item_id:
                            lists[iList]["items"][iItem]["status"] = status
                            self.data["lists"] = lists
                            "HA doesn't think the list changed so set it to none first..."
                            hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", None)
                            hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", self.data)
                            break
                            break
        except KeyError as ex:
            LOGGER.warning(ex)

    async def local_remove_items(
        self, 
        hass: HomeAssistant, 
        list_id: str, 
        item_ids: []
        ) -> None:
        try:
            lists = hass.data[DOMAIN]["lists"]
            for iList, item in enumerate(lists):
                if item["listId"] == list_id:
                    for iItem, item in enumerate(item["items"]):
                        if item["itemId"] in item_ids:
                            del lists[iList]["items"][iItem]
                    self.data["lists"] = lists
                    "HA doesn't think the list changed so set it to none first..."
                    hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", None)
                    hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", self.data)
                    break
        except KeyError as ex:
            LOGGER.warning(ex)

    async def local_reorder_list(
        self, 
        hass: HomeAssistant, 
        list_id: str,
        items_list: []
        ) -> None:
        try:
            lists = hass.data[DOMAIN]["lists"]
            for iList, item in enumerate(lists):
                if item["listId"] == list_id:
                    lists[iList]["items"] = items_list
                    self.data["lists"] = lists
                    "HA doesn't think the list changed so set it to none first..."
                    hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", None)
                    hass.states.async_set("sensor.{}_lists".format(DOMAIN), "", self.data)
                    break
        except KeyError as ex:
            LOGGER.warning(ex)