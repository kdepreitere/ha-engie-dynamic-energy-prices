# Engie Dynamic Prices — Home Assistant Integration

A Home Assistant custom component that fetches EPEX day-ahead spot prices published by Engie Belgium and exposes them as sensors with optional contract formula applied.

## Features

- **Hourly spot prices** (today & tomorrow) — current, next, min, max, average
- **15-minute spot prices** (today & tomorrow) — current, next, average, min, max
- **Contract buy price** — applies your personal tariff formula on top of spot
- **Contract sell price** — spot minus your injection fee
- **Binary sensors** — alerts when spot or sell price goes negative
- Prices update every 15 minutes; HTTP fetches only happen when new data is needed
- Tomorrow's prices become available after ~14:00 (when EPEX publishes them)

## Installation

### HACS (recommended)

1. Add this repository as a custom HACS repository (type: Integration).
2. Search for **Engie Dynamic Prices** and install.
3. Restart Home Assistant.

### Manual

1. Copy the `custom_components/engie_dynamic_prices` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

Go to **Settings → Devices & Services → Add Integration** and search for **Engie Dynamic Prices**.

You will be asked to enter four contract parameters that determine your actual buy and sell prices:

| Parameter | Description | Default |
|---|---|---|
| `buy_multiplier` | Spot price multiplier in the buy formula | `1.019` |
| `buy_energy_fee` | Fixed energy component added per kWh (EUR/kWh) | `0.010617` |
| `buy_distribution_fee` | Distribution/transport tariff (EUR/kWh) | `0.20` |
| `sell_fee` | Fee subtracted from spot for injection (EUR/kWh) | `0.012965` |

**Buy price formula:**
```
contract_buy = (buy_multiplier × spot + buy_energy_fee) + buy_distribution_fee
```

**Sell price formula:**
```
contract_sell = spot − sell_fee
```

You can update these values at any time via **Settings → Devices & Services → Engie Dynamic Prices → Configure**.

## Sensors

### Today — spot (hourly)

| Entity | Description |
|---|---|
| `sensor.engie_current_price` | Current hour spot price (EUR/kWh). Attributes: all 24 hourly prices, negative hours. |
| `sensor.engie_next_price` | Next hour spot price |
| `sensor.engie_average_price` | Today's average spot price. Attributes: cheapest hours ranked. |
| `sensor.engie_min_price` | Today's minimum spot price (based on 15-min granularity) |
| `sensor.engie_max_price` | Today's maximum spot price |

### Today — contract buy (hourly)

| Entity | Description |
|---|---|
| `sensor.engie_current_contract_price` | Current hour buy price after formula. Attributes: formula string. |
| `sensor.engie_next_contract_price` | Next hour buy price |
| `sensor.engie_average_contract_price` | Today's average contract buy price |
| `sensor.engie_min_contract_price` | Today's minimum contract buy price |
| `sensor.engie_max_contract_price` | Today's maximum contract buy price |

### Today — sell price (hourly)

| Entity | Description |
|---|---|
| `sensor.engie_current_sell_price` | Current hour sell price. Attributes: formula string, negative sell hours. |
| `sensor.engie_next_sell_price` | Next hour sell price |
| `sensor.engie_average_sell_price` | Today's average sell price |
| `sensor.engie_min_sell_price` | Today's minimum sell price |
| `sensor.engie_max_sell_price` | Today's maximum sell price |

### Today — 15-minute granularity

| Entity | Description |
|---|---|
| `sensor.engie_current_price_15min` | Current 15-min slot spot price. Attributes: all 96 slots, negative slots. |
| `sensor.engie_next_price_15min` | Next 15-min slot spot price |
| `sensor.engie_current_contract_price_15min` | Current 15-min buy price after formula. Attributes: all 96 buy slots. |
| `sensor.engie_current_sell_price_15min` | Current 15-min sell price. Attributes: all 96 sell slots. |

### Tomorrow — spot (hourly, available after ~14:00)

| Entity | Description |
|---|---|
| `sensor.engie_tomorrow_average_price` | Tomorrow's average spot price. Attributes: cheapest hours, all 24 prices, negative hours. |
| `sensor.engie_tomorrow_min_price` | Tomorrow's minimum spot price |
| `sensor.engie_tomorrow_max_price` | Tomorrow's maximum spot price |

### Tomorrow — contract buy / sell (hourly)

| Entity | Description |
|---|---|
| `sensor.engie_tomorrow_average_contract_price` | Tomorrow's average contract buy price |
| `sensor.engie_tomorrow_min_contract_price` | Tomorrow's minimum contract buy price |
| `sensor.engie_tomorrow_max_contract_price` | Tomorrow's maximum contract buy price |
| `sensor.engie_tomorrow_average_sell_price` | Tomorrow's average sell price |
| `sensor.engie_tomorrow_min_sell_price` | Tomorrow's minimum sell price |
| `sensor.engie_tomorrow_max_sell_price` | Tomorrow's maximum sell price |

### Tomorrow — 15-minute granularity

| Entity | Description |
|---|---|
| `sensor.engie_tomorrow_average_price_15min` | Tomorrow's average 15-min spot price. Attributes: all 96 slots, negative slots. |
| `sensor.engie_tomorrow_min_price_15min` | Tomorrow's minimum 15-min spot price |
| `sensor.engie_tomorrow_max_price_15min` | Tomorrow's maximum 15-min spot price |

## Binary Sensors

| Entity | On when… |
|---|---|
| `binary_sensor.engie_buy_price_negative` | Current hourly spot price < 0 EUR/kWh |
| `binary_sensor.engie_sell_price_negative` | Current sell price < −0.02 EUR/kWh (you pay to inject) |
| `binary_sensor.engie_buy_price_15min_negative` | Current 15-min spot price < 0 EUR/kWh |
| `binary_sensor.engie_tomorrow_has_negative_prices` | Tomorrow has at least one negative hourly spot price |

All binary sensors use device class `problem` so they appear as warnings in the HA UI.

## Requirements

- Home Assistant 2024.1.0 or newer
- Python package: `openpyxl >= 3.1.0` (installed automatically)

## Data Source

Prices are fetched from the public Engie Belgium EPEX export endpoint. The XLSX file contains quarter-hour (15-min) prices for a single day. Before ~14:00 the file holds today's prices; after ~14:00 it switches to tomorrow's. The coordinator keeps both sets in memory so today's prices remain available after the switch.
