import logging
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from datetime import datetime
import requests
import json
from homeassistant.helpers.update_coordinator import CoordinatorEntity


_LOGGER = logging.getLogger(__name__)

# Definition der Plattformkonfiguration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

import logging
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup sensor platform."""
    # Hole die spezifische Konfiguration für 'evcharger'
    evcharger_config = config.get('evcharger')
    if evcharger_config is None:
        _LOGGER.error("EVCharger Konfiguration nicht gefunden.")
        return  # Frühzeitiger Abbruch, wenn keine Konfiguration gefunden wird

    # Hole Benutzername und Passwort aus der Konfiguration
    username = evcharger_config.get(CONF_USERNAME)
    password = evcharger_config.get(CONF_PASSWORD)
    if username is None or password is None:
        _LOGGER.error("Benutzername oder Passwort nicht in der Konfiguration gefunden.")
        return  # Frühzeitiger Abbruch, wenn kritische Daten fehlen

    # Hole den Coordinator aus den gespeicherten Daten
    coordinator = hass.data["evcharger"]["coordinator"]

    # Füge die Sensorentitäten zur Home Assistant Instanz hinzu
    add_entities([EvchargerSensor(coordinator, username, password)], True)  # True sorgt für ein Update beim Hinzufügen




class evchargerSensor(CoordinatorEntity, SensorEntity):
    """Definition des evcharger Sensors."""

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
        return "evchargerSensor"

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
