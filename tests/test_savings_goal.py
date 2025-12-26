"""Unit tests for savings goal model."""

import unittest
from datetime import date, timedelta
from src.models.currency import Currency, Money
from src.models.savings_goal import SavingsGoal, GoalStatus


class TestSavingsGoal(unittest.TestCase):
    """Test SavingsGoal class."""

    def test_goal_creation(self):
        """Test creating a savings goal."""
        target = Money(1000, Currency.USD)
        goal = SavingsGoal(
            name="Emergency Fund",
            target_amount=target,
            description="6 months expenses"
        )

        self.assertEqual(goal.name, "Emergency Fund")
        self.assertEqual(goal.target_amount, target)
        self.assertEqual(goal.current_amount.amount, 0)
        self.assertEqual(goal.description, "6 months expenses")

    def test_goal_progress_percentage(self):
        """Test progress percentage calculation."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        self.assertEqual(goal.progress_percentage, 0.0)

        goal.add_savings(Money(250, Currency.USD))
        self.assertEqual(goal.progress_percentage, 25.0)

        goal.add_savings(Money(750, Currency.USD))
        self.assertEqual(goal.progress_percentage, 100.0)

    def test_remaining_amount(self):
        """Test remaining amount calculation."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        self.assertEqual(goal.remaining_amount.amount, 1000)

        goal.add_savings(Money(300, Currency.USD))
        self.assertEqual(goal.remaining_amount.amount, 700)

    def test_goal_status_not_started(self):
        """Test NOT_STARTED status."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        self.assertEqual(goal.status, GoalStatus.NOT_STARTED)

    def test_goal_status_in_progress(self):
        """Test IN_PROGRESS status."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        goal.add_savings(Money(100, Currency.USD))
        self.assertEqual(goal.status, GoalStatus.IN_PROGRESS)

    def test_goal_status_completed(self):
        """Test COMPLETED status."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        goal.add_savings(Money(1000, Currency.USD))
        self.assertEqual(goal.status, GoalStatus.COMPLETED)

    def test_goal_status_overdue(self):
        """Test OVERDUE status."""
        yesterday = date.today() - timedelta(days=1)
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD),
            deadline=yesterday
        )

        goal.add_savings(Money(100, Currency.USD))
        self.assertEqual(goal.status, GoalStatus.OVERDUE)

    def test_days_remaining(self):
        """Test days remaining calculation."""
        future_date = date.today() + timedelta(days=30)
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD),
            deadline=future_date
        )

        self.assertEqual(goal.days_remaining, 30)

    def test_days_remaining_no_deadline(self):
        """Test days remaining without deadline."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        self.assertIsNone(goal.days_remaining)

    def test_daily_savings_needed(self):
        """Test daily savings calculation."""
        future_date = date.today() + timedelta(days=10)
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD),
            deadline=future_date
        )

        daily = goal.daily_savings_needed()
        self.assertIsNotNone(daily)
        self.assertEqual(daily.amount, 100.0)  # 1000 / 10 days

    def test_add_savings(self):
        """Test adding savings to goal."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        initial_amount = goal.current_amount.amount
        goal.add_savings(Money(250, Currency.USD))

        self.assertEqual(goal.current_amount.amount, initial_amount + 250)

    def test_add_savings_wrong_currency(self):
        """Test adding savings in wrong currency raises error."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        with self.assertRaises(ValueError):
            goal.add_savings(Money(250, Currency.GBP))

    def test_withdraw(self):
        """Test withdrawing from savings."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        goal.add_savings(Money(500, Currency.USD))
        goal.withdraw(Money(200, Currency.USD))

        self.assertEqual(goal.current_amount.amount, 300)

    def test_withdraw_too_much(self):
        """Test withdrawing more than available raises error."""
        goal = SavingsGoal(
            name="Test Goal",
            target_amount=Money(1000, Currency.USD)
        )

        goal.add_savings(Money(100, Currency.USD))

        with self.assertRaises(ValueError):
            goal.withdraw(Money(200, Currency.USD))


if __name__ == "__main__":
    unittest.main()
