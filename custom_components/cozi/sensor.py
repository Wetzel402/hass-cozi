"""Support for Cozi service."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import callback
from .entity import CoziEntity

from .const import DOMAIN, SENSOR_PERSONS, SENSOR_LISTS

async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            PersonsSensor(
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=SENSOR_PERSONS,
                    name=SENSOR_PERSONS,
                ),
            ),
            ListsSensor(
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key=SENSOR_LISTS,
                    name=SENSOR_LISTS,
                ),
            ),
        ]
    )

class PersonsSensor(CoziEntity, SensorEntity):
    """Persons returned from Cozi"""

    _attr_icon = "mdi:account-group"
    _attr_native_unit_of_measurement = "persons"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        if self.coordinator.data:
            return ""
        else:
            return self._attr_native_value

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "persons": self.coordinator.data["persons"],
                "updated": self.coordinator.data["last_update"],
                }
        else:
            return {}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data:
            self._attr_native_value = ""
            self._attr_extra_state_attributes = {
                "persons": self.coordinator.data["persons"],
                "updated": self.coordinator.data["last_update"],
            }
            self.async_write_ha_state()
        super()._handle_coordinator_update()

class ListsSensor(CoziEntity, SensorEntity):
    """Lists returned from Cozi"""

    _attr_icon = "mdi:format-list-bulleted-square"
    _attr_native_unit_of_measurement = "list"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        if self.coordinator.data:
            return ""
        else:
            return self._attr_native_value

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                "lists": self.coordinator.data["lists"],
                "updated": self.coordinator.data["last_update"],
                }
        else:
            return {}

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data:
            self._attr_native_value = ""
            self._attr_extra_state_attributes = {
                "lists": self.coordinator.data["lists"],
                "updated": self.coordinator.data["last_update"],
            }
            self.async_write_ha_state()
        super()._handle_coordinator_update()