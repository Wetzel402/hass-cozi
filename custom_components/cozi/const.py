"""Constants for the Cozi component."""
import logging

from datetime import timedelta

LOGGER = logging.getLogger(__package__)

VERSION = '1.0.0'
DOMAIN = "cozi"
ATTRIBUTION = "Data provided by cozi.com"
HELP_URL = "https://www.home-assistant.io/components/cozi"

UPDATE_INTERVAL = timedelta(seconds=300)

SENSOR_PERSONS = "cozi_persons"
SENSOR_LISTS = "cozi_lists"