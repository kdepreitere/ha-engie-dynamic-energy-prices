"""Engie Dynamic Prices integration for Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change

from .const import (
    CONF_BUY_DISTRIBUTION_FEE,
    CONF_BUY_ENERGY_FEE,
    CONF_BUY_MULTIPLIER,
    CONF_SELL_FEE,
)
from .coordinator import EngieCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Engie Dynamic Prices from a config entry."""
    session = async_get_clientsession(hass)

    coordinator = EngieCoordinator(
        hass,
        session,
        buy_multiplier=entry.data.get(CONF_BUY_MULTIPLIER, 1.019),
        buy_energy_fee=entry.data.get(CONF_BUY_ENERGY_FEE, 0.010617),
        buy_distribution_fee=entry.data.get(CONF_BUY_DISTRIBUTION_FEE, 0.20),
        sell_fee=entry.data.get(CONF_SELL_FEE, 0.012965),
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Refresh every 15 minutes so 15-min price sensors stay current.
    # The coordinator uses slot-based caching -- actual HTTP fetches happen at
    # most twice a day (morning + 14:00 for tomorrow's day-ahead prices).
    async def _refresh_on_quarter(now) -> None:
        await coordinator.async_refresh()

    entry.async_on_unload(
        async_track_time_change(
            hass, _refresh_on_quarter, minute=[0, 15, 30, 45], second=0
        )
    )

    # Reload when formula parameters are updated via the options flow.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
