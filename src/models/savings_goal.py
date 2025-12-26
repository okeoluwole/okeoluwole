"""Savings goal model."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum
from .currency import Money, Currency


class GoalStatus(Enum):
    """Status of a savings goal."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"


@dataclass
class SavingsGoal:
    """Represents a savings goal."""
    name: str
    target_amount: Money
    current_amount: Money = None
    deadline: Optional[date] = None
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.current_amount is None:
            self.current_amount = Money(0, self.target_amount.currency)

        # Ensure currencies match
        if self.current_amount.currency != self.target_amount.currency:
            raise ValueError("Current amount and target amount must be in the same currency")

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.target_amount.amount == 0:
            return 100.0
        return min((self.current_amount.amount / self.target_amount.amount) * 100, 100.0)

    @property
    def remaining_amount(self) -> Money:
        """Calculate remaining amount to reach goal."""
        remaining = self.target_amount.amount - self.current_amount.amount
        return Money(max(remaining, 0), self.target_amount.currency)

    @property
    def status(self) -> GoalStatus:
        """Determine current status of the goal."""
        if self.current_amount.amount >= self.target_amount.amount:
            return GoalStatus.COMPLETED

        if self.deadline:
            if date.today() > self.deadline:
                return GoalStatus.OVERDUE

        if self.current_amount.amount > 0:
            return GoalStatus.IN_PROGRESS

        return GoalStatus.NOT_STARTED

    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until deadline."""
        if self.deadline is None:
            return None
        delta = self.deadline - date.today()
        return delta.days

    def add_savings(self, amount: Money) -> None:
        """Add savings to the goal."""
        if amount.currency != self.current_amount.currency:
            raise ValueError("Amount currency must match goal currency")

        self.current_amount = self.current_amount + amount

    def withdraw(self, amount: Money) -> None:
        """Withdraw from savings."""
        if amount.currency != self.current_amount.currency:
            raise ValueError("Amount currency must match goal currency")

        if amount.amount > self.current_amount.amount:
            raise ValueError("Cannot withdraw more than current savings")

        self.current_amount = self.current_amount - amount

    def daily_savings_needed(self) -> Optional[Money]:
        """Calculate daily savings needed to meet goal by deadline."""
        if self.deadline is None or self.days_remaining is None or self.days_remaining <= 0:
            return None

        remaining = self.remaining_amount.amount
        daily_amount = remaining / self.days_remaining

        return Money(daily_amount, self.target_amount.currency)
