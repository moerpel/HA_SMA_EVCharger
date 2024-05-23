import requests
import json
from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)

class EvChargerAPI:
    def __init__(self, api_url, username, password):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None

    def authenticate(self):
        """Authenticate and obtain a token for subsequent API calls."""
        token_url = f"{self.api_url}/api/v1/token"
        auth_payload = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }

        response = self.session.post(token_url, data=auth_payload)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        tokens = response.json()
        self.token = tokens.get("access_token")

        if not self.token:
            raise ValueError("Authentication failed, no token received")

        # Update session headers with the received token
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_data(self):
        """Fetch the data from the API."""
        measurements_url = f"{self.api_url}/api/v1/measurements/live/"
        payload = json.dumps([{"componentId": "IGULD:SELF"}])

        response = self.session.post(measurements_url, data=payload)
        response.raise_for_status()
        data = response.json()

        # Log the entire response for debugging
        _LOGGER.debug(f"API response: {json.dumps(data, indent=2)}")

        # Data Processing
        current_power = None
        total_energy = None

        for item in data:
            channel = item['channelId']
            time_and_value = item['values']

            # Ensure time_and_value is a list and contains at least one valid measurement
            if not isinstance(time_and_value, list) or len(time_and_value) == 0:
                _LOGGER.error(f"Unexpected data format: {time_and_value}")
                continue

            # Process the latest measurement in time_and_value
            latest_measurement = time_and_value[-1]
            datetime_str = latest_measurement.get('time')
            value = latest_measurement.get('value')

            if datetime_str is None or value is None:
                _LOGGER.warning(f"Skipping incomplete measurement: {latest_measurement}")
                continue

            try:
                datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                value = float(value)
            except ValueError as e:
                _LOGGER.error(f"Error parsing values: {e}")
                continue

            if channel == "Measurement.ChaSess.WhIn":
                total_energy = value / 1000  # Convert to kWh
            elif channel == "Measurement.Metering.GridMs.TotWIn":
                current_power = value / 1000  # Convert to kW

            # Log the parsed values for debugging
            _LOGGER.debug(f"Channel: {channel}, Current Power: {current_power}, Total Energy: {total_energy}")

        if current_power is None or total_energy is None:
            _LOGGER.error("Failed to retrieve necessary data from the API response")
            _LOGGER.debug(f"Final parsed values - Current Power: {current_power}, Total Energy: {total_energy}")
            raise ValueError("Failed to retrieve necessary data from the API response")

        return {
            "current_power": current_power,
            "total_energy": total_energy
        }
