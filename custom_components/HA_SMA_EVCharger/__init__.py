import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_URL
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from functools import partial
from datetime import timedelta
import logging
import requests
import json

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Optional('evcharger'): vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required('base_url'): cv.url,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the component from configuration.yaml."""
    conf = config.get('evcharger')
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="evcharger_coordinator",
        update_method=lambda: update_data(hass, conf),
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data["evcharger"] = {
        "coordinator": coordinator,
        "config": conf
    }

    hass.async_create_task(
        hass.helpers.discovery.async_load_platform('sensor', 'evcharger', {}, config)
    )

    return True

async def update_data(hass: HomeAssistant, conf):
    """Fetch data from API."""
    base_url = conf['base_url']
    username = conf['username']
    password = conf['password']

    token_url = f'{base_url}/api/v1/token'
    # Prepare the data and headers outside the async_add_executor_job call
    data = {'grant_type': 'password', 'username': username, 'password': password}

    # Correct the use of async_add_executor_job for requests.post
    response = await hass.async_add_executor_job(
        requests.post, token_url, data
    )

    # Check the response and proceed similarly for the other requests
    if response.status_code != 200:
        _LOGGER.error("Failed to fetch token: %s", response.text)
        raise UpdateFailed(f"Error fetching token: {response.status_code}")

    tokens = response.json()
    access_token = tokens['access_token']

    measurements_url = f'{base_url}/api/v1/measurements/live/'
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = json.dumps([{"componentId": "IGULD:SELF"}])

    # Again, ensure that async_add_executor_job is used correctly
    
    post = partial(requests.post, measurements_url, headers=headers, data=payload)
    measurements_response = await hass.async_add_executor_job(post)

    if measurements_response.status_code != 200:
        _LOGGER.error("Failed to fetch measurements: %s", measurements_response.text)
        raise UpdateFailed(f"Error fetching measurements: {measurements_response.status_code}")

    return measurements_response.json()
