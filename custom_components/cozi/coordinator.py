"""Data update coordinator for Cozi"""
from __future__ import annotations

import logging

from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant as hass
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from cozi import Cozi
from cozi.exceptions import InvalidLoginException

from .const import DOMAIN, LOGGER
from .sensor import PersonsSensor, ListsSensor

class CoziCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, logger, name, update_interval):
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=name,  # Name of the data. For logging purposes.
            update_interval=update_interval,
        )
        self.hass = hass
        self.data = {}

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint and map data."""

        """persons sensor"""
        person_attrs = []
        try:
            persons = await self.hass.data[DOMAIN]["init"].cozi.get_persons()
            for item in persons:
                LOGGER.debug(item)
                person_attrs.append(
                {
                    "name": item["name"],
                    "accountPersonId": item["accountPersonId"],
                }
            )
            self.hass.data[DOMAIN]["persons"] = person_attrs
        except TypeError:
            LOGGER.warning("TypeError thrown likely due to expired token.  Cozi will attempt a login.")
        except InvalidLoginException as ex:
            raise ConfigEntryAuthFailed(f"Invalid credentials: {ex}") from ex

        """lists sensor"""
        lists_attrs = []
        try:
            lists = await self.hass.data[DOMAIN]["init"].cozi.get_lists()
            for item in lists:
                LOGGER.debug(item)
                lists_attrs.append(
                {
                    "title": item["title"],
                    "listId": item["listId"],
                    "listType": item["listType"],
                    "items": item["items"],
                }
            )
            self.hass.data[DOMAIN]["lists"] = lists_attrs
        except TypeError:
            LOGGER.warning("TypeError thrown likely due to expired token.  Cozi will attempt a login.")
        except InvalidLoginException as ex:
            raise ConfigEntryAuthFailed(f"Invalid credentials: {ex}") from ex

        self.hass.data[DOMAIN]["last_update"] = dt_util.now()

        self.data = {
            "persons": person_attrs,
            "lists": lists_attrs,
            "last_update": self.hass.data[DOMAIN]["last_update"],
        }

        self.hass.bus.fire("cozi_updated")
        LOGGER.debug("Cozi sensors updated")

        return self.data