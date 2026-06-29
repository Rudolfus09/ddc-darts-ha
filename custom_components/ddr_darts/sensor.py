from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import DDRDartsCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([
        DDRDartsLastEventSensor(coordinator, entry),
        DDRDartsConnectionSensor(coordinator, entry),
    ])


class DDRDartsLastEventSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "last_event"

    def __init__(self, coordinator: DDRDartsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_event"
        self._attr_name = "DDR Darts Letzter Event"
        self._last_event_type = None
        self._last_player = None

    @callback
    def _handle_coordinator_update(self):
        events = self.coordinator.data.get("events", []) if self.coordinator.data else []
        if events:
            last = events[-1]
            self._last_event_type = last.get("event_type")
            self._last_player = last.get("player")
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._last_event_type

    @property
    def extra_state_attributes(self):
        return {"player": self._last_player}


class DDRDartsConnectionSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: DDRDartsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_connection"
        self._attr_name = "DDR Darts Verbindung"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "Unbekannt"
        if self.coordinator.data.get("error"):
            return "Fehler"
        return "Verbunden"

    @property
    def icon(self):
        val = self.native_value
        if val == "Verbunden":
            return "mdi:dartboard"
        return "mdi:dartboard-variant"
