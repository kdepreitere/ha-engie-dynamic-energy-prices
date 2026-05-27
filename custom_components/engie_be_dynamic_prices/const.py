"""Constants for the Engie Dynamic Prices integration."""

DOMAIN = "engie_be_dynamic_prices"

# Buy price formula:  contract_buy = (BUY_MULTIPLIER * spot + BUY_ENERGY_FEE) + BUY_DISTRIBUTION_FEE
CONF_BUY_MULTIPLIER       = "buy_multiplier"
CONF_BUY_ENERGY_FEE       = "buy_energy_fee"
CONF_BUY_DISTRIBUTION_FEE = "buy_distribution_fee"

# Sell price formula: contract_sell = spot - SELL_FEE
CONF_SELL_FEE = "sell_fee"

# Binary sensor threshold: sell price alert fires when sell price < this value (EUR/kWh)
SELL_ALERT_THRESHOLD = -0.02

# EPEX day-ahead prices published by Engie (~14:00 each day).
XLSX_URL = "https://www.engie.be/api/engie/be/ms/pricing/public/v1/epex-prices/export?exportType=XLSX"
