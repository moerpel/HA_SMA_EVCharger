import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from datetime import datetime
import requests
import json
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# Definition der Plattformkonfiguration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup sensor platform."""
    coordinator = hass.data["your_integration"]
    add_entities([YourSensor(coordinator, config[CONF_USERNAME], config[CONF_PASSWORD])])

class YourSensor(CoordinatorEntity, SensorEntity):
    """Definition des Custom Sensors."""

    def __init__(self, coordinator, username, password):
        """Initialisieren des Sensors."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._username = username
        self._password = password
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Rückgabe des Namens des Sensors."""
        return "Custom Sensor"

    @property
    def state(self):
        """Rückgabe des aktuellen Sensorzustands."""
        # Beispiel zur Verwendung der Daten; spezifische Logik hier anpassen
        if self.coordinator.data:
            return float(self.coordinator.data[14]['values']) / 1000 if self.coordinator.data[14]['values'] else None
        return None

    @property
    def extra_state_attributes(self):
        """Rückgabe zusätzlicher Attribute des Sensors."""
        # Weitere nützliche Informationen als Attribute hinzufügen
        if self.coordinator.data:
            return {
                'aktuelle_ladung': float(self.coordinator.data[0]['values']) / 1000 if self.coordinator.data[0]['values'] else None,
                'zeitstempel': datetime.now().isoformat()
            }
        return {}
