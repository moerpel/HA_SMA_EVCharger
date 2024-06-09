

# HA_SMA_EVCharger
A first test of retrieving data from EvCharger in Home Assistant.

## Installation
1. Add https://github.com/moerpel/HA_SMA_EVCharger as repository in HACS
2. Install SMA EV Charger from list.

## Configuration
add the following to the configuration.yaml in your Home Assistant configuration
```yaml
evcharger:
    username: "your username to access EV Charger WebPortal"
    password: "your password to access EV Charger WebPortal"
    api_url: "http://IP_Address_of_Wallbox"
```
## Restart your Home Assistant

## Sensor Entities that will be available in Homeassistant:
    sensor.evcharger_charging_status_raw > represents the raw value of the EVCharger that defines the charging status.
    sensor.evcharger_charging_status > represents the charging status of the charger, which is derived from sensor.evcharger_charging_status_raw and can have the following values: 'charging', 'sleeping', 'not connected'

    sensor.evcharger_connection_status_raw > represents the raw value of the EVCharger that defines the overall status of the wallbox.
    sensor.evcharger_connection_status > represents the overall connection status of the wallbox, which is derived from sensor.evcharger_connection_status_raw and can have the following values: "ok
