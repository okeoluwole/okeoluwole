"""Currency models and definitions."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict


class Currency(Enum):
    """Supported currencies."""
    SAR = "SAR"  # Saudi Riyal
    USD = "USD"  # United States Dollar
    GBP = "GBP"  # British Pound
    NGN = "NGN"  # Nigerian Naira

    def __str__(self):
        return self.value


@dataclass
class CurrencyInfo:
    """Currency information."""
    code: str
    name: str
    symbol: str
    country: str


CURRENCY_INFO: Dict[Currency, CurrencyInfo] = {
    Currency.SAR: CurrencyInfo("SAR", "Saudi Riyal", "﷼", "Saudi Arabia"),
    Currency.USD: CurrencyInfo("USD", "US Dollar", "$", "United States"),
    Currency.GBP: CurrencyInfo("GBP", "British Pound", "£", "United Kingdom"),
    Currency.NGN: CurrencyInfo("NGN", "Nigerian Naira", "₦", "Nigeria"),
}


@dataclass
class Money:
    """Represents an amount in a specific currency."""
    amount: float
    currency: Currency

    def __str__(self):
        info = CURRENCY_INFO[self.currency]
        return f"{info.symbol}{self.amount:,.2f} {self.currency.value}"

    def __add__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Can only add Money objects")
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies without conversion")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money objects")
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies without conversion")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, scalar):
        return Money(self.amount * scalar, self.currency)

    def __truediv__(self, scalar):
        return Money(self.amount / scalar, self.currency)

    def __lt__(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies without conversion")
        return self.amount < other.amount

    def __gt__(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies without conversion")
        return self.amount > other.amount

    def __eq__(self, other):
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
