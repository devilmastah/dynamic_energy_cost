"""Class representing a Dynamic Energy Costs config flow."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.exceptions import ConfigValidationError
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

INIT_SCHEMA= vol.Schema(
            {
                vol.Optional("integration_description"): selector.TextSelector(),
                vol.Required("electricity_price_sensor"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional("power_sensor"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor", multiple=False, device_class="power"
                    )
                ),
                vol.Optional("energy_sensor"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor", multiple=False, device_class="energy"
                    )
                ),
            }
        )

CHANGE_INIT_SCHEMA = vol.Schema(
            {
                vol.Required(
                    "electricity_price_sensor",
                    default=current_values.get("electricity_price_sensor"),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", multiple=False)
                ),
                vol.Optional(
                    "power_sensor", default=current_values.get("power_sensor")
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor", multiple=False, device_class="power"
                    )
                ),
                vol.Optional(
                    "energy_sensor", default=current_values.get("energy_sensor")
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor", multiple=False, device_class="energy"
                    )
                ),
            }
        )



class DynamicEnergyCostConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dynamic Energy Cost."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.debug("Initiating config flow for user")
        errors = {}

        if user_input is not None:
            _LOGGER.info("Received user input: %s", user_input)
            try:
                # Validate the electricity price sensor
                cv.entity_id(user_input["electricity_price_sensor"])
                if user_input.get("power_sensor"):
                    cv.entity_id(user_input["power_sensor"])
                if user_input.get("energy_sensor"):
                    cv.entity_id(user_input["energy_sensor"])

                # Check that either power sensor or energy sensor is filled
                if not user_input.get("power_sensor") and not user_input.get(
                    "energy_sensor"
                ):
                    _LOGGER.warning("Neither power nor energy sensor was provided")
                    raise ConfigValidationError(
                        "Please enter either a power sensor or an energy sensor, not both."
                    )
                if user_input.get("power_sensor") and user_input.get("energy_sensor"):
                    _LOGGER.warning("Both power and energy sensors were provided")
                    raise ConfigValidationError(
                        "Please enter only one type of sensor (power or energy)."
                    )

                # Create the config dictionary
                config = {
                    "electricity_price_sensor": user_input["electricity_price_sensor"],
                    "power_sensor": user_input.get("power_sensor"),
                    "energy_sensor": user_input.get("energy_sensor"),
                    "integration_description": user_input.get(
                        "integration_description", "Unnamed"
                    ),
                }
                _LOGGER.info("Config entry created successfully")
                return self.async_create_entry(
                    title=f"Dynamic Energy Cost - {user_input.get('integration_description', 'Unnamed')}",
                    data=config,
                )
            except vol.Invalid as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = "invalid_entity"

        

        return self.async_show_form(
            step_id="user",
            data_schema=INIT_SCHEMA,
            errors=errors,
            description_placeholders={
                "integration_description": "Name to append the integration title",
                "electricity_price_sensor": "Electricity Price Sensor",
                "power_sensor": "Power Usage Sensor",
                "energy_sensor": "Energy (kWh) Sensor",
            },
        )

    # Change existing config added !!
    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DynamicEnergyCostOptionsFlow(config_entry)


# Change existing config added !!
class DynamicEnergyCostOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for DynamicEnergyCost."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # Get the current values from the config entry
        current_values = self.config_entry.data

        

        return self.async_show_form(
            step_id="user",
            data_schema=CHANGE_INIT_SCHEMA,
            errors=errors,
        )
