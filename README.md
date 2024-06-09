

# HA_SMA_EVCharger
A first attempt of retrieving data from EvCharger in Home Assistant.

## Installation
1. Add https://github.com/moerpel/HA_SMA_EVCharger as repository in HACS
2. Install SMA EV Charger from list.

## Configuration
add the following to the configuration.yaml in your Home Assistant configuration
```yaml
evcharger:
    username: "your username to access EV Charger WebPortal"
    password: "your password to access EV Charger WebPortal"
    api_url: "http://IP_Address_of_Wallbox" # Example: "http://192.168.178.123"
```

## Restart your Home Assistant

## Sensor entities that will be available in Homeassistant:
    sensor.evcharger_charging_status_raw > represents the raw value of the EVCharger that defines the charging status.
    sensor.evcharger_charging_status > represents the charging status of the charger, which is derived from sensor.evcharger_charging_status_raw and can have the following values: 'charging', 'sleeping', 'not connected'

    sensor.evcharger_connection_status_raw > represents the raw value of the EVCharger that defines the overall status of the wallbox.
    sensor.evcharger_connection_status > represents the overall connection status of the wallbox, which is derived from sensor.evcharger_connection_status_raw and can have the following values: 'ok', 'warning', 'alert', 'off'.

    sensor.evcharger_current_charging_power > this entity represents the current charging power.

    sensor.evcharger_energy_counter_charging_station > this entitty represents the value of the total energy counter of the wallbox.

    sensor.evcharger_mode_switch > represents the raw value of the physical switch.
    sensor.evcharger_mode _ this entitiy represents the position of the physical switch and can have the following values 'fast charging', 'intelligent charging', 'unknown'.

    sensor.evcharger_total_energy_charged > represents the value of the energy counter for this charging session.

    
<img width="1336" alt="image" src="https://github.com/moerpel/HA_SMA_EVCharger/assets/66588833/2bad1445-e6fe-4df6-9530-aef503e5532b">
