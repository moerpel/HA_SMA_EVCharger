from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up the component."""
    # Coordinator einrichten
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="your_integration_coordinator",
        update_method=update_data,
        update_interval=timedelta(seconds=30),
    )

    # Daten initial abrufen
    await coordinator.async_refresh()

    # Sensorplattform laden und Coordinator weitergeben
    hass.data["your_integration"] = coordinator
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform('sensor', 'your_integration', {}, config)
    )

    return True

async def update_data():
    """Fetch data from API."""
    token_url = 'http://192.168.178.97/api/v1/token'
    response = await hass.async_add_executor_job(
        requests.post, token_url, {'grant_type': 'password', 'username': 'kmsiedler', 'password': 'Reldeis.23'}
    )
    tokens = response.json()
    access_token = tokens['access_token']
    
    measurements_url = 'http://192.168.178.97/api/v1/measurements/live/'
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = json.dumps([{"componentId": "IGULD:SELF"}])
    
    measurements_response = await hass.async_add_executor_job(
        requests.post, measurements_url, headers=headers, data=payload
    )
    data = measurements_response.json()
    
    if measurements_response.status_code != 200:
        raise UpdateFailed(f"Error fetching data: {measurements_response.status_code}, {measurements_response.text}")

    return data
