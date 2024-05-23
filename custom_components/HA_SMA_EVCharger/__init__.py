import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.discovery import load_platform

DOMAIN = "evcharger"
CONF_API_URL = "api_url"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_API_URL): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    """Set up the SMA EV Charger component."""
    conf = config[DOMAIN]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    api_url = conf[CONF_API_URL]

    hass.data[DOMAIN] = {
        CONF_USERNAME: username,
        CONF_PASSWORD: password,
        CONF_API_URL: api_url,
    }

    load_platform(hass, "sensor", DOMAIN, {}, config)

    return True
