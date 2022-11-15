"""Constants for the Cozi component."""
import logging

from datetime import timedelta

LOGGER = logging.getLogger(__package__)

VERSION = '2022.11.0'
DOMAIN = "cozi"
ATTRIBUTION = "Data provided by cozi.com"
HELP_URL = "https://github.com/Wetzel402/hass-cozi"

UPDATE_INTERVAL = timedelta(seconds=300)

SENSOR_PERSONS = "cozi_persons"
SENSOR_LISTS = "cozi_lists"