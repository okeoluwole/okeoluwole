"""Exchange rate service for currency conversion."""

import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..models.currency import Currency, Money


class ExchangeRateService:
    """Handles currency exchange rates and conversions."""

    def __init__(self):
        self.base_currency = Currency.USD
        self.rates: Dict[str, float] = {}
        self.last_updated: Optional[datetime] = None
        self.cache_duration = timedelta(hours=1)

        # Fallback rates (approximate, as of late 2024)
        self.fallback_rates = {
            "SAR": 3.75,  # SAR per USD
            "USD": 1.0,   # Base currency
            "GBP": 0.79,  # GBP per USD
            "NGN": 1650.0,  # NGN per USD
        }

    def fetch_rates(self) -> bool:
        """Fetch latest exchange rates from API."""
        try:
            # Using exchangerate-api.com free tier
            response = requests.get(
                "https://api.exchangerate-api.com/v4/latest/USD",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.rates = data.get("rates", {})
                self.last_updated = datetime.now()
                return True
        except Exception as e:
            print(f"Warning: Could not fetch live rates: {e}")

        # Use fallback rates
        self.rates = self.fallback_rates.copy()
        self.last_updated = datetime.now()
        return False

    def get_rate(self, from_currency: Currency, to_currency: Currency) -> float:
        """Get exchange rate from one currency to another."""
        # Refresh rates if needed
        if (self.last_updated is None or
            datetime.now() - self.last_updated > self.cache_duration):
            self.fetch_rates()

        if from_currency == to_currency:
            return 1.0

        # Convert through USD as base
        from_rate = self.rates.get(from_currency.value, self.fallback_rates[from_currency.value])
        to_rate = self.rates.get(to_currency.value, self.fallback_rates[to_currency.value])

        return to_rate / from_rate

    def convert(self, money: Money, to_currency: Currency) -> Money:
        """Convert money from one currency to another."""
        if money.currency == to_currency:
            return money

        rate = self.get_rate(money.currency, to_currency)
        converted_amount = money.amount * rate

        return Money(converted_amount, to_currency)

    def get_all_rates(self, base: Currency = Currency.USD) -> Dict[Currency, float]:
        """Get all exchange rates relative to a base currency."""
        if (self.last_updated is None or
            datetime.now() - self.last_updated > self.cache_duration):
            self.fetch_rates()

        result = {}
        for currency in Currency:
            result[currency] = self.get_rate(base, currency)

        return result

    def is_rates_live(self) -> bool:
        """Check if using live rates or fallback."""
        return self.last_updated is not None and len(self.rates) > 4
