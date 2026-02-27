"""Unit tests for currency models."""

import unittest
from src.models.currency import Currency, Money, CURRENCY_INFO


class TestCurrency(unittest.TestCase):
    """Test currency enum and info."""

    def test_currency_values(self):
        """Test currency enum values."""
        self.assertEqual(Currency.SAR.value, "SAR")
        self.assertEqual(Currency.USD.value, "USD")
        self.assertEqual(Currency.GBP.value, "GBP")
        self.assertEqual(Currency.NGN.value, "NGN")

    def test_currency_info(self):
        """Test currency information."""
        usd_info = CURRENCY_INFO[Currency.USD]
        self.assertEqual(usd_info.code, "USD")
        self.assertEqual(usd_info.name, "US Dollar")
        self.assertEqual(usd_info.symbol, "$")
        self.assertEqual(usd_info.country, "United States")


class TestMoney(unittest.TestCase):
    """Test Money class operations."""

    def test_money_creation(self):
        """Test creating Money objects."""
        money = Money(100.0, Currency.USD)
        self.assertEqual(money.amount, 100.0)
        self.assertEqual(money.currency, Currency.USD)

    def test_money_string_representation(self):
        """Test Money string representation."""
        money = Money(1500.50, Currency.SAR)
        self.assertIn("﷼", str(money))
        self.assertIn("1,500.50", str(money))
        self.assertIn("SAR", str(money))

    def test_money_addition(self):
        """Test adding Money objects."""
        money1 = Money(100, Currency.USD)
        money2 = Money(50, Currency.USD)
        result = money1 + money2
        self.assertEqual(result.amount, 150)
        self.assertEqual(result.currency, Currency.USD)

    def test_money_addition_different_currencies(self):
        """Test that adding different currencies raises error."""
        money1 = Money(100, Currency.USD)
        money2 = Money(50, Currency.GBP)
        with self.assertRaises(ValueError):
            _ = money1 + money2

    def test_money_subtraction(self):
        """Test subtracting Money objects."""
        money1 = Money(100, Currency.USD)
        money2 = Money(30, Currency.USD)
        result = money1 - money2
        self.assertEqual(result.amount, 70)
        self.assertEqual(result.currency, Currency.USD)

    def test_money_multiplication(self):
        """Test multiplying Money by scalar."""
        money = Money(100, Currency.USD)
        result = money * 1.5
        self.assertEqual(result.amount, 150)
        self.assertEqual(result.currency, Currency.USD)

    def test_money_division(self):
        """Test dividing Money by scalar."""
        money = Money(100, Currency.USD)
        result = money / 2
        self.assertEqual(result.amount, 50)
        self.assertEqual(result.currency, Currency.USD)

    def test_money_comparison(self):
        """Test comparing Money objects."""
        money1 = Money(100, Currency.USD)
        money2 = Money(50, Currency.USD)
        money3 = Money(100, Currency.USD)

        self.assertTrue(money1 > money2)
        self.assertTrue(money2 < money1)
        self.assertTrue(money1 == money3)

    def test_money_comparison_different_currencies(self):
        """Test that comparing different currencies raises error."""
        money1 = Money(100, Currency.USD)
        money2 = Money(50, Currency.GBP)
        with self.assertRaises(ValueError):
            _ = money1 > money2


if __name__ == "__main__":
    unittest.main()
