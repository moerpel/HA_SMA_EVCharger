import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPower, UnitOfEnergy
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from .evcharger_requests import EvChargerAPI
from . import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_API_URL

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the SMA EV Charger sensors."""
    if discovery_info is None:
        return

    username = hass.data[DOMAIN][CONF_USERNAME]
    password = hass.data[DOMAIN][CONF_PASSWORD]
    api_url = hass.data[DOMAIN][CONF_API_URL]

    api = EvChargerAPI(api_url, username, password)

    await hass.async_add_executor_job(api.authenticate)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="evcharger",
        update_method=lambda: hass.async_add_executor_job(api.get_data),
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        EvChargerPowerSensor(coordinator),
        EvChargerEnergySensor(coordinator),
        EvChargerConnectionStatusRaw(coordinator),
        EvChargerModeSwitch(coordinator),
        EvChargerMode(coordinator),
        EvChargerChargingStatusRaw(coordinator),
        EvChargerChargingStatus(coordinator),
        EvChargerEnergyCounterChargingStation(coordinator),
        EvChargerConnectionStatus(coordinator)
    ])

class EvChargerSensor(CoordinatorEntity, SensorEntity):
    """Base class for EV Charger sensors."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_state = None

    @property
    def available(self):
        """Return if sensor is available."""
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()

class EvChargerPowerSensor(EvChargerSensor):
    """Sensor for current charging power."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Current Charging Power"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_current_power")

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfPower.KILO_WATT

class EvChargerEnergySensor(EvChargerSensor):
    """Sensor for total energy charged."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Total Energy Charged"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_total_energy")

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR
class EvChargerConnectionStatusRaw(EvChargerSensor):
    """Sensor for total connection status raw."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Connection Status Raw"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_connection_status_raw")
class EvChargerModeSwitch(EvChargerSensor):
    """Sensor for Mode Switch"""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Mode Switch"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_mode_switch")
class EvChargerMode(EvChargerSensor):
    """Sensor for Mode."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Mode"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_mode")
class EvChargerChargingStatusRaw(EvChargerSensor):
    """Sensor for Charging Status Raw value."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Charging Status Raw"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_charging_status_raw")

class EvChargerChargingStatus(EvChargerSensor):
    """Sensor for Charging status."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Charging Status"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_charging_status")
class EvChargerEnergyCounterChargingStation(EvChargerSensor):
    """Sensor for Energy Counter Charging Station."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Energy Counter Charging Station"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_energy_counter_ChargingStation_total_Wh")
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

class EvChargerConnectionStatus(EvChargerSensor):
    """Sensor for Connection Status value."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return "EVcharger Connection Status"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("evcharger_connection_status")
