"""Multi-currency portfolio model."""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
from .currency import Currency, Money
from .savings_goal import SavingsGoal


@dataclass
class Transaction:
    """Represents a financial transaction."""
    amount: Money
    transaction_type: str  # 'deposit', 'withdrawal', 'transfer'
    description: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CurrencyAccount:
    """Represents an account in a specific currency."""
    currency: Currency
    balance: Money
    transactions: List[Transaction] = field(default_factory=list)

    def __post_init__(self):
        if self.balance.currency != self.currency:
            raise ValueError("Balance currency must match account currency")

    def deposit(self, amount: Money, description: str = "") -> None:
        """Deposit money into the account."""
        if amount.currency != self.currency:
            raise ValueError("Deposit currency must match account currency")

        self.balance = self.balance + amount
        self.transactions.append(Transaction(amount, "deposit", description))

    def withdraw(self, amount: Money, description: str = "") -> None:
        """Withdraw money from the account."""
        if amount.currency != self.currency:
            raise ValueError("Withdrawal currency must match account currency")

        if amount.amount > self.balance.amount:
            raise ValueError("Insufficient funds")

        self.balance = self.balance - amount
        self.transactions.append(Transaction(amount, "withdrawal", description))


@dataclass
class Portfolio:
    """Multi-currency portfolio manager."""
    name: str
    accounts: Dict[Currency, CurrencyAccount] = field(default_factory=dict)
    savings_goals: List[SavingsGoal] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # Initialize accounts for all supported currencies
        for currency in Currency:
            if currency not in self.accounts:
                self.accounts[currency] = CurrencyAccount(
                    currency=currency,
                    balance=Money(0, currency)
                )

    def get_account(self, currency: Currency) -> CurrencyAccount:
        """Get account for a specific currency."""
        return self.accounts[currency]

    def deposit(self, amount: Money, description: str = "") -> None:
        """Deposit money into the appropriate currency account."""
        account = self.get_account(amount.currency)
        account.deposit(amount, description)

    def withdraw(self, amount: Money, description: str = "") -> None:
        """Withdraw money from the appropriate currency account."""
        account = self.get_account(amount.currency)
        account.withdraw(amount, description)

    def get_total_balance_in(self, target_currency: Currency, exchange_service) -> Money:
        """Get total portfolio balance in a specific currency."""
        total = Money(0, target_currency)

        for account in self.accounts.values():
            if account.balance.amount > 0:
                converted = exchange_service.convert(account.balance, target_currency)
                total = total + converted

        return total

    def add_savings_goal(self, goal: SavingsGoal) -> None:
        """Add a savings goal to the portfolio."""
        self.savings_goals.append(goal)

    def remove_savings_goal(self, goal_name: str) -> bool:
        """Remove a savings goal by name."""
        for i, goal in enumerate(self.savings_goals):
            if goal.name == goal_name:
                self.savings_goals.pop(i)
                return True
        return False

    def get_savings_goal(self, goal_name: str) -> SavingsGoal:
        """Get a savings goal by name."""
        for goal in self.savings_goals:
            if goal.name == goal_name:
                return goal
        raise ValueError(f"Savings goal '{goal_name}' not found")

    def contribute_to_goal(self, goal_name: str, amount: Money) -> None:
        """Contribute to a savings goal."""
        goal = self.get_savings_goal(goal_name)
        account = self.get_account(amount.currency)

        # Withdraw from account
        account.withdraw(amount, f"Contribution to goal: {goal_name}")

        # Add to goal (convert if necessary)
        if amount.currency != goal.target_amount.currency:
            raise ValueError("Currency conversion needed - implement exchange service")

        goal.add_savings(amount)

    def get_balance_breakdown(self) -> Dict[Currency, Money]:
        """Get balance breakdown by currency."""
        return {
            currency: account.balance
            for currency, account in self.accounts.items()
        }

    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions across all accounts."""
        all_transactions = []
        for account in self.accounts.values():
            all_transactions.extend(account.transactions)

        # Sort by timestamp
        return sorted(all_transactions, key=lambda t: t.timestamp, reverse=True)
