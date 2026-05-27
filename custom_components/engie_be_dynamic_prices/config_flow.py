"""Config flow for Engie Dynamic Prices."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback

from .const import (
    CONF_BUY_DISTRIBUTION_FEE,
    CONF_BUY_ENERGY_FEE,
    CONF_BUY_MULTIPLIER,
    CONF_SELL_FEE,
    DOMAIN,
)

# Defaults matching the user's contract:
#   buy  = (1.019 * spot + 0.010617) + 0.20
#   sell = spot - 0.012965
_DEFAULT_BUY_MULTIPLIER       = 1.019
_DEFAULT_BUY_ENERGY_FEE       = 0.010617
_DEFAULT_BUY_DISTRIBUTION_FEE = 0.20
_DEFAULT_SELL_FEE              = 0.012965


def _formula_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_BUY_MULTIPLIER,
                default=defaults.get(CONF_BUY_MULTIPLIER, _DEFAULT_BUY_MULTIPLIER),
            ): vol.Coerce(float),
            vol.Required(
                CONF_BUY_ENERGY_FEE,
                default=defaults.get(CONF_BUY_ENERGY_FEE, _DEFAULT_BUY_ENERGY_FEE),
            ): vol.Coerce(float),
            vol.Required(
                CONF_BUY_DISTRIBUTION_FEE,
                default=defaults.get(CONF_BUY_DISTRIBUTION_FEE, _DEFAULT_BUY_DISTRIBUTION_FEE),
            ): vol.Coerce(float),
            vol.Required(
                CONF_SELL_FEE,
                default=defaults.get(CONF_SELL_FEE, _DEFAULT_SELL_FEE),
            ): vol.Coerce(float),
        }
    )


class EngieConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Engie Dynamic Prices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(title="Engie Dynamic Prices", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_formula_schema({}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> EngieOptionsFlow:
        return EngieOptionsFlow(config_entry)


class EngieOptionsFlow(OptionsFlow):
    """Allow updating the formula parameters without removing the integration."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={**self._config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=_formula_schema(self._config_entry.data),
        )
