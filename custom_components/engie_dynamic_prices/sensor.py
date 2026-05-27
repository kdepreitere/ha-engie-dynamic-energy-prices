"""Sensor entities for Engie Dynamic Prices."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EngieCoordinator, EngieData

PRICE_UNIT = "EUR/kWh"


@dataclass(frozen=True, kw_only=True)
class EngieSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[EngieData], float | None]
    extra_attrs_fn: Callable[[EngieData], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[EngieSensorEntityDescription, ...] = (
    # -------------------------------------------------------- today -- spot hourly
    EngieSensorEntityDescription(
        key="current_price",
        translation_key="current_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.current_price,
        extra_attrs_fn=lambda d: {
            "all_prices_today": d.all_prices_today,
            "negative_hours_today": d.negative_price_hours_today,
        },
    ),
    EngieSensorEntityDescription(
        key="next_price",
        translation_key="next_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.next_price,
    ),
    EngieSensorEntityDescription(
        key="average_price",
        translation_key="average_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.average_price,
        extra_attrs_fn=lambda d: {"cheapest_hours": d.cheapest_hours},
    ),
    EngieSensorEntityDescription(
        key="min_price",
        translation_key="min_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.min_price,
    ),
    EngieSensorEntityDescription(
        key="max_price",
        translation_key="max_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.max_price,
    ),
    # ----------------------------------------- today -- buy (contract) hourly
    EngieSensorEntityDescription(
        key="current_contract_price",
        translation_key="current_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.current_contract_price,
        extra_attrs_fn=lambda d: {
            "formula": f"({d.buy_multiplier} * spot + {d.buy_energy_fee}) + {d.buy_distribution_fee}",
        },
    ),
    EngieSensorEntityDescription(
        key="next_contract_price",
        translation_key="next_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.next_contract_price,
    ),
    EngieSensorEntityDescription(
        key="average_contract_price",
        translation_key="average_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.average_contract_price,
    ),
    EngieSensorEntityDescription(
        key="min_contract_price",
        translation_key="min_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.min_contract_price,
    ),
    EngieSensorEntityDescription(
        key="max_contract_price",
        translation_key="max_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.max_contract_price,
    ),
    # ---------------------------------------------------- today -- sell hourly
    EngieSensorEntityDescription(
        key="current_sell_price",
        translation_key="current_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.current_sell_price,
        extra_attrs_fn=lambda d: {
            "formula": f"spot - {d.sell_fee}",
            "negative_sell_hours_today": d.negative_sell_hours_today,
        },
    ),
    EngieSensorEntityDescription(
        key="next_sell_price",
        translation_key="next_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.next_sell_price,
    ),
    EngieSensorEntityDescription(
        key="average_sell_price",
        translation_key="average_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.average_sell_price,
    ),
    EngieSensorEntityDescription(
        key="min_sell_price",
        translation_key="min_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.min_sell_price,
    ),
    EngieSensorEntityDescription(
        key="max_sell_price",
        translation_key="max_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.max_sell_price,
    ),
    # -------------------------------------------------- today -- 15-min spot
    EngieSensorEntityDescription(
        key="current_price_15min",
        translation_key="current_price_15min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.current_price_15min,
        extra_attrs_fn=lambda d: {
            "all_prices_15min_today": d.all_prices_15min_today,
            "negative_slots_today": d.negative_price_slots_today,
        },
    ),
    EngieSensorEntityDescription(
        key="next_price_15min",
        translation_key="next_price_15min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.next_price_15min,
    ),
    # ---------------------------------------- today -- 15-min contract / sell
    EngieSensorEntityDescription(
        key="current_contract_price_15min",
        translation_key="current_contract_price_15min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.current_contract_price_15min,
        extra_attrs_fn=lambda d: {
            "all_contract_prices_15min_today": [
                {"slot": s["slot"], "price_eur_kwh": d._buy(s["price_eur_kwh"])}
                for s in d.all_prices_15min_today
            ],
        },
    ),
    EngieSensorEntityDescription(
        key="current_sell_price_15min",
        translation_key="current_sell_price_15min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.current_sell_price_15min,
        extra_attrs_fn=lambda d: {
            "all_sell_prices_15min_today": [
                {"slot": s["slot"], "price_eur_kwh": d._sell(s["price_eur_kwh"])}
                for s in d.all_prices_15min_today
            ],
        },
    ),
    # ----------------------------------------- tomorrow -- spot hourly
    EngieSensorEntityDescription(
        key="tomorrow_average_price",
        translation_key="tomorrow_average_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_average_price,
        extra_attrs_fn=lambda d: {
            "cheapest_hours_tomorrow": d.tomorrow_cheapest_hours,
            "all_prices_tomorrow": d.all_prices_tomorrow,
            "negative_hours_tomorrow": d.negative_price_hours_tomorrow,
        },
    ),
    EngieSensorEntityDescription(
        key="tomorrow_min_price",
        translation_key="tomorrow_min_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_min_price,
    ),
    EngieSensorEntityDescription(
        key="tomorrow_max_price",
        translation_key="tomorrow_max_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_max_price,
    ),
    # ------------------------------------- tomorrow -- contract / sell hourly
    EngieSensorEntityDescription(
        key="tomorrow_average_contract_price",
        translation_key="tomorrow_average_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_average_contract_price,
    ),
    EngieSensorEntityDescription(
        key="tomorrow_min_contract_price",
        translation_key="tomorrow_min_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_min_contract_price,
    ),
    EngieSensorEntityDescription(
        key="tomorrow_max_contract_price",
        translation_key="tomorrow_max_contract_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_max_contract_price,
    ),
    EngieSensorEntityDescription(
        key="tomorrow_average_sell_price",
        translation_key="tomorrow_average_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_average_sell_price,
    ),
    EngieSensorEntityDescription(
        key="tomorrow_min_sell_price",
        translation_key="tomorrow_min_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_min_sell_price,
    ),
    EngieSensorEntityDescription(
        key="tomorrow_max_sell_price",
        translation_key="tomorrow_max_sell_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_max_sell_price,
    ),
    # ----------------------------------------------- tomorrow -- 15-min spot
    EngieSensorEntityDescription(
        key="tomorrow_average_price_15min",
        translation_key="tomorrow_average_price_15min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_average_price_15min,
        extra_attrs_fn=lambda d: {
            "all_prices_15min_tomorrow": d.all_prices_15min_tomorrow,
            "negative_slots_tomorrow": d.negative_price_slots_tomorrow,
        },
    ),
    EngieSensorEntityDescription(
        key="tomorrow_min_price_15min",
        translation_key="tomorrow_min_price_15min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_min_price_15min,
    ),
    EngieSensorEntityDescription(
        key="tomorrow_max_price_15min",
        translation_key="tomorrow_max_price_15min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda d: d.tomorrow_max_price_15min,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EngieCoordinator = entry.runtime_data
    async_add_entities(
        EngieSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class EngieSensor(CoordinatorEntity[EngieCoordinator], SensorEntity):
    entity_description: EngieSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: EngieCoordinator, description: EngieSensorEntityDescription) -> None:
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
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.coordinator.data is None or self.entity_description.extra_attrs_fn is None:
            return None
        return self.entity_description.extra_attrs_fn(self.coordinator.data)
