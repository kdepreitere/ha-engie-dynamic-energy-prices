"""Binary sensor entities for Engie Dynamic Prices."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EngieCoordinator, EngieData


@dataclass(frozen=True, kw_only=True)
class EngieBinarySensorEntityDescription(BinarySensorEntityDescription):
    is_on_fn: Callable[[EngieData], bool]
    extra_attrs_fn: Callable[[EngieData], dict[str, Any]] | None = None


BINARY_SENSOR_DESCRIPTIONS: tuple[EngieBinarySensorEntityDescription, ...] = (
    # Spot buy price negative -- grid pays you to consume
    EngieBinarySensorEntityDescription(
        key="buy_price_negative",
        translation_key="buy_price_negative",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.is_current_price_negative,
        extra_attrs_fn=lambda d: {
            "current_spot_price_eur_kwh": d.current_price,
            "negative_hours_today": d.negative_price_hours_today,
            "negative_hours_tomorrow": d.negative_price_hours_tomorrow,
        },
    ),
    # Sell price below -0.02 EUR/kWh -- you pay to inject
    EngieBinarySensorEntityDescription(
        key="sell_price_negative",
        translation_key="sell_price_negative",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.is_current_sell_price_negative,
        extra_attrs_fn=lambda d: {
            "current_sell_price_eur_kwh": d.current_sell_price,
            "sell_fee_eur_kwh": d.sell_fee,
            "negative_sell_hours_today": d.negative_sell_hours_today,
            "tomorrow_has_negative_sell_prices": d.tomorrow_has_negative_sell_prices,
        },
    ),
    # 15-min spot price negative
    EngieBinarySensorEntityDescription(
        key="buy_price_15min_negative",
        translation_key="buy_price_15min_negative",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.is_current_price_15min_negative,
        extra_attrs_fn=lambda d: {
            "current_price_15min_eur_kwh": d.current_price_15min,
            "negative_slots_today": d.negative_price_slots_today,
            "negative_slots_tomorrow": d.negative_price_slots_tomorrow,
        },
    ),
    # Tomorrow has at least one negative-price hour (useful for planning)
    EngieBinarySensorEntityDescription(
        key="tomorrow_has_negative_prices",
        translation_key="tomorrow_has_negative_prices",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: d.tomorrow_has_negative_prices,
        extra_attrs_fn=lambda d: {
            "negative_hours_tomorrow": d.negative_price_hours_tomorrow,
            "tomorrow_min_price_eur_kwh": d.tomorrow_min_price,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EngieCoordinator = entry.runtime_data
    async_add_entities(
        EngieBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class EngieBinarySensor(CoordinatorEntity[EngieCoordinator], BinarySensorEntity):
    entity_description: EngieBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EngieCoordinator,
        description: EngieBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, DOMAIN)},
            name="Engie Dynamic Prices",
            manufacturer="Engie",
        )

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.is_on_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.coordinator.data is None or self.entity_description.extra_attrs_fn is None:
            return None
        return self.entity_description.extra_attrs_fn(self.coordinator.data)
