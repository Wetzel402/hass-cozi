"""Constants for the Cozi component."""
import pathlib
import logging
import json

from datetime import timedelta
from homeassistant.core import Config as hass

p = pathlib.PurePath(pathlib.Path(__file__).parent.resolve(), 'manifest.json')
f = open(p)
manifest = json.load(f)

LOGGER = logging.getLogger(__package__)

VERSION = manifest['version']
DOMAIN = manifest['domain']
ATTRIBUTION = "Data provided by cozi.com"
HELP_URL = manifest['documentation']

UPDATE_INTERVAL = timedelta(seconds=300)

SENSOR_PERSONS = "cozi_persons"
SENSOR_LISTS = "cozi_lists"