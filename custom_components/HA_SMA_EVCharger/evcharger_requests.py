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
        self.access_token = None
        self.refresh_token = None

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
        self.access_token = tokens.get("access_token")
        _LOGGER.debug(f"Access Token: {self.access_token}")
        self.refresh_token = tokens.get("refresh_token")
        _LOGGER.debug(f"Refresh Token: {self.refresh_token}")

        if not self.access_token:
            raise ValueError("Authentication failed, no token received")

        # Update session headers with the received token
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

    def get_data(self):
        """Refresh token to have a valid authentication."""
        _LOGGER.info(f"Fetching data from wallbox {self.api_url}.")
        refresh_payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        token_url = f"{self.api_url}/api/v1/token"
        response = self.session.post(token_url, data=refresh_payload)
        _LOGGER.info(f"Result: {response}")
        _LOGGER.debug(f"Refresh Token Used: {self.refresh_token}")

        """Fetch the data from the API."""
        measurements_url = f"{self.api_url}/api/v1/measurements/live/"
        payload = json.dumps([{"componentId": "IGULD:SELF"}])

        response = self.session.post(measurements_url, data=payload)
        response.raise_for_status()
        data = response.json()

        # Log the entire response for debugging
        #_LOGGER.debug(f"API response: {json.dumps(data, indent=2)}")

        # Data Processing
        evcharger_current_power = None
        evcharger_total_energy = None
        evcharger_connection_status_raw = None
        evcharger_mode_switch = None
        evcharger_mode = None
        evcharger_charging_status_raw = None
        evcharger_charging_status = None
        evcharger_energy_counter_ChargingStation_total_Wh = None
        evcharger_connection_status = None

        for item in data:
            channel = item['channelId']
            time_and_value = item['values']

            # Ensure time_and_value is a list and contains at least one valid measurement
            if not isinstance(time_and_value, list) or len(time_and_value) == 0:
                _LOGGER.error(f"Unexpected data format: {time_and_value}")
                continue
            #print(channel)
            # Process the latest measurement in time_and_value
            latest_measurement = time_and_value[-1]
            #print(latest_measurement)
            datetime_str = latest_measurement.get('time')
            #print(datetime_str)
            value = latest_measurement.get('value')
            #print(value)

            ''' if datetime_str is None or value is None:
                _LOGGER.warning(f"Skipping incomplete measurement: {latest_measurement}")
                continue

            try:
                datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                value = float(value)
            except ValueError as e:
                _LOGGER.error(f"Error parsing values: {e}")
                continue '''

            if channel == "Measurement.ChaSess.WhIn":
                evcharger_total_energy = value / 1000  # Convert to kWh
            elif channel == "Measurement.Metering.GridMs.TotWIn":
                evcharger_current_power = value / 1000  # Convert to kW
            elif channel == "Measurement.Operation.EVeh.Health":
                evcharger_connection_status_raw = value   # Connection Status
                _LOGGER.debug(f"{evcharger_connection_status_raw}")

            elif channel == "Measurement.Chrg.ModSw":
                evcharger_mode_switch = value   # Mode Switch
            elif channel == "Measurement.Operation.EVeh.ChaStt":
                evcharger_charging_status_raw = value   # Charging Status
            elif channel == "Measurement.Metering.GridMs.TotWhIn.ChaSta":
                evcharger_energy_counter__ChargingStation_total_Wh = value / 1000 # Energy Counter overall charging station Convert to kWh
        
        if evcharger_current_power is None or evcharger_total_energy is None or evcharger_connection_status_raw is None or evcharger_mode_switch is None:
            _LOGGER.error("Failed to retrieve necessary data from the API response")
            _LOGGER.debug(f"Final parsed values - Current Power: {evcharger_current_power}, Total Energy: {evcharger_total_energy}, Connection Status: {evcharger_connection_status_raw}")
            raise ValueError("Failed to retrieve necessary data from the API response")
        # Log the parsed values for debugging
        _LOGGER.debug(f"Channel: {channel}, Current Power: {evcharger_current_power}, Total Energy: {evcharger_total_energy}, Connection Status: {evcharger_connection_status_raw}, Mode Switch: {evcharger_mode_switch}")
        
        #Translations
        if str(evcharger_mode_switch) == "4950":
            evcharger_mode ="intelligent charging"    
        elif str(evcharger_mode_switch) == "4718":
            evcharger_mode ="fast charging" 
        else: evcharger_mode = "unknown"

        _LOGGER.debug(f"Translated evcharger switch position raw: {evcharger_mode_switch} to readable: {evcharger_mode}")
        
        if str(evcharger_charging_status_raw) == "200111":
            evcharger_charging_status ="not connected"    
        elif str(evcharger_charging_status_raw) == "200112":
            evcharger_charging_status = "sleeping"
        elif str(evcharger_charging_status_raw) == "200113":
                evcharger_charging_status = "charging"
        else: evcharger_charging_status = "unknown"
        _LOGGER.debug(f"Translated evcharger charging status raw: {evcharger_charging_status_raw} to readable: {evcharger_charging_status}")
        if str(evcharger_connection_status_raw) == "307":
            evcharger_connection_status ="ok"    
        elif str(evcharger_connection_status_raw) == "455":
            evcharger_connection_status = "warning"
        elif str(evcharger_connection_status_raw) == "35":
                evcharger_connection_status = "alert"
        elif str(evcharger_connection_status_raw) == "303":
                evcharger_connection_status = "off"
        else: evcharger_connection_status = "unknown"
        _LOGGER.debug(f"Translated evcharger connection status raw: {evcharger_connection_status_raw} to readable: {evcharger_connection_status}")

        return {
            "evcharger_current_power": evcharger_current_power,
            "evcharger_total_energy": evcharger_total_energy,
            "evcharger_connection_status_raw": evcharger_connection_status_raw,
            "evcharger_mode_switch": evcharger_mode_switch,
            "evcharger_mode": evcharger_mode,
            "evcharger_charging_status_raw": evcharger_charging_status_raw,
            "evcharger_charging_status": evcharger_charging_status,
            "evcharger_energy_counter_ChargingStation_total_Wh": evcharger_energy_counter_ChargingStation_total_Wh,
            "evcharger_connection_status": evcharger_connection_status
        }
