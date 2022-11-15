"""Represents Cozi service in the device registry of Home Assistant"""

from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .const import DOMAIN, VERSION, HELP_URL


class CoziEntity(CoordinatorEntity):
    """Representation of a Cozi entity."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        # per sensor unique_id
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "cozi_unique_id")},
            manufacturer="Wetzel402",
            model="Cozi for HA",
            name="Cozi",
            sw_version=VERSION,
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=HELP_URL,
        )
        self._attr_extra_state_attributes = {}