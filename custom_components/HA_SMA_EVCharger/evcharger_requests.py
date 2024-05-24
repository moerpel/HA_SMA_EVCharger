import requests
import json
from datetime import datetime, timedelta
import logging

_LOGGER = logging.getLogger(__name__)

class EvChargerAPI:
    def __init__(self, api_url, username, password):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        self.refresh_token = None
        self.token_expiry = None

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
        self.refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 3600)  # Default to 1 hour if not provided
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

        if not self.token or not self.refresh_token:
            raise ValueError("Authentication failed, no token received")

        # Update session headers with the received token
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        refresh_url = f"{self.api_url}/api/v1/token"
        refresh_payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        response = self.session.post(refresh_url, data=refresh_payload)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        tokens = response.json()
        self.token = tokens.get("access_token")
        expires_in = tokens.get("expires_in", 3600)  # Default to 1 hour if not provided
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

        if not self.token:
            raise ValueError("Failed to refresh access token")

        # Update session headers with the new access token
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def ensure_token_valid(self):
        """Ensure the access token is valid, refresh if necessary."""
        if self.token_expiry is None or datetime.now() >= self.token_expiry:
            self.refresh_access_token()

    def get_data(self):
        """Fetch the data from the API."""
        self.ensure_token_valid()  # Ensure the access token is valid before making the request

        measurements_url = f"{self.api_url}/api/v1/measurements/live/"
        payload = json.dumps([{"componentId": "IGULD:SELF"}])

        response = self.session.post(measurements_url, data=payload)
        response.raise_for_status()
        data = response.json()

        # Log the entire response for debugging
        _LOGGER.debug(f"API response: {json.dumps(data, indent=2)}")

        # Data Processing
        evcharger_current_power = None
        evcharger_total_energy = None
        evcharger_mod_sw = None

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
                evcharger_total_energy = value / 1000  # Convert to kWh
            elif channel == "Measurement.Metering.GridMs.TotWIn":
                evcharger_current_power = value / 1000  # Convert to kW
            elif channel == "Measurement.Metering.Chrg.ModSw":
                evcharger_mod_sw = value

            # Log the parsed values for debugging
            _LOGGER.debug(f"Channel: {channel}, Current Power: {evcharger_current_power}, Total Energy: {evcharger_total_energy}, ModSw: {evcharger_mod_sw}")

        if evcharger_current_power is None or evcharger_total_energy is None or evcharger_mod_sw is None:
            _LOGGER.error("Failed to retrieve necessary data from the API response")
            _LOGGER.debug(f"Final parsed values - Current Power: {evcharger_current_power}, Total Energy: {evcharger_total_energy}, ModSw: {evcharger_mod_sw}")
            raise ValueError("Failed to retrieve necessary data from the API response")

        return {
            "evcharger_current_power": evcharger_current_power,
            "evcharger_total_energy": evcharger_total_energy,
            "evcharger_mod_sw": evcharger_mod_sw
        }
