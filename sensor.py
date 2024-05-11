import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from datetime import datetime
import requests
import json

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    add_entities([YourSensor(username, password)])

class YourSensor(SensorEntity):
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._state = None

    @property
    def name(self):
        return 'Custom Sensor'

    @property
    def state(self):
        return self._state

    def update(self):
    token_url = f'http://192.168.178.97/api/v1/token'
    response = requests.post(token_url, data={'grant_type': 'password', 'username': self._username, 'password': self._password})
    tokens = response.json()
    access_token = tokens['access_token']
    
    measurements_url = 'http://192.168.178.97/api/v1/measurements/live/'
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = json.dumps([{"componentId": "IGULD:SELF"}])
    measurements_response = requests.post(measurements_url, headers=headers, data=payload)
    data = measurements_response.json()
    
    if data:  # Stelle sicher, dass Daten vorhanden sind
        # Angenommen, wir sind interessiert an einem spezifischen Wert, wie 'aktuelle Ladeleistung'
        ladeleistung = float(data[14]['values']) / 1000  # Angenommen, dies ist der richtige Index und das Format
        self._state = ladeleistung  # Zustand des Sensors ist die Ladeleistung
        self._attributes = {
            'aktuelle_ladung': float(data[0]['values']) / 1000,
            'zeitstempel': datetime.now().isoformat()
        }

