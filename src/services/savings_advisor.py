"""Savings advisor engine for providing financial recommendations."""

from typing import List, Dict, Tuple
from datetime import date, timedelta
from ..models.currency import Currency, Money
from ..models.portfolio import Portfolio
from ..models.savings_goal import SavingsGoal, GoalStatus
from .exchange_rate_service import ExchangeRateService


class Recommendation:
    """Represents a financial recommendation."""

    def __init__(self, title: str, description: str, priority: str, savings_impact: Money = None):
        self.title = title
        self.description = description
        self.priority = priority  # 'high', 'medium', 'low'
        self.savings_impact = savings_impact

    def __str__(self):
        impact = f" (Impact: {self.savings_impact})" if self.savings_impact else ""
        return f"[{self.priority.upper()}] {self.title}: {self.description}{impact}"


class SavingsAdvisor:
    """Provides intelligent savings advice based on portfolio and goals."""

    def __init__(self, portfolio: Portfolio, exchange_service: ExchangeRateService):
        self.portfolio = portfolio
        self.exchange_service = exchange_service

    def analyze_portfolio(self) -> Dict[str, any]:
        """Analyze portfolio and provide insights."""
        analysis = {
            "total_balance_usd": self.portfolio.get_total_balance_in(Currency.USD, self.exchange_service),
            "currency_breakdown": self.portfolio.get_balance_breakdown(),
            "active_goals": len([g for g in self.portfolio.savings_goals if g.status == GoalStatus.IN_PROGRESS]),
            "completed_goals": len([g for g in self.portfolio.savings_goals if g.status == GoalStatus.COMPLETED]),
            "overdue_goals": len([g for g in self.portfolio.savings_goals if g.status == GoalStatus.OVERDUE]),
        }

        return analysis

    def get_currency_recommendations(self) -> List[Recommendation]:
        """Get recommendations based on currency holdings and exchange rates."""
        recommendations = []

        balances = self.portfolio.get_balance_breakdown()
        rates = self.exchange_service.get_all_rates(Currency.USD)

        # Check for currency concentration risk
        total_usd = self.portfolio.get_total_balance_in(Currency.USD, self.exchange_service)
        if total_usd.amount > 0:
            for currency, balance in balances.items():
                if balance.amount > 0:
                    balance_usd = self.exchange_service.convert(balance, Currency.USD)
                    percentage = (balance_usd.amount / total_usd.amount) * 100

                    if percentage > 70:
                        recommendations.append(Recommendation(
                            title="High Currency Concentration",
                            description=f"You have {percentage:.1f}% of your savings in {currency.value}. "
                                      f"Consider diversifying across multiple currencies to reduce risk.",
                            priority="medium"
                        ))

        # Check for low-performing currencies
        weak_currencies = self._identify_weak_currencies()
        if weak_currencies:
            for currency in weak_currencies:
                balance = balances.get(currency)
                if balance and balance.amount > 100:  # Only recommend if significant balance
                    recommendations.append(Recommendation(
                        title=f"Consider Converting {currency.value}",
                        description=f"Consider converting some {currency.value} holdings to stronger "
                                  f"currencies like USD or GBP for better value preservation.",
                        priority="low"
                    ))

        return recommendations

    def get_goal_recommendations(self) -> List[Recommendation]:
        """Get recommendations based on savings goals."""
        recommendations = []

        for goal in self.portfolio.savings_goals:
            if goal.status == GoalStatus.OVERDUE:
                recommendations.append(Recommendation(
                    title=f"Overdue Goal: {goal.name}",
                    description=f"Your goal '{goal.name}' is overdue. "
                              f"You still need {goal.remaining_amount} to reach your target. "
                              f"Consider revising the deadline or adjusting the target amount.",
                    priority="high"
                ))

            elif goal.status == GoalStatus.IN_PROGRESS and goal.deadline:
                days_remaining = goal.days_remaining
                daily_needed = goal.daily_savings_needed()

                if days_remaining and days_remaining <= 30 and goal.progress_percentage < 50:
                    recommendations.append(Recommendation(
                        title=f"Goal at Risk: {goal.name}",
                        description=f"Only {days_remaining} days left to reach '{goal.name}' "
                                  f"but you're only {goal.progress_percentage:.1f}% complete. "
                                  f"You need to save {daily_needed} per day to meet your goal.",
                        priority="high",
                        savings_impact=daily_needed
                    ))

                elif days_remaining and days_remaining > 30 and daily_needed:
                    recommendations.append(Recommendation(
                        title=f"Stay on Track: {goal.name}",
                        description=f"To reach '{goal.name}' by your deadline, "
                                  f"save {daily_needed} per day.",
                        priority="medium",
                        savings_impact=daily_needed
                    ))

        # Check for no active goals
        if not self.portfolio.savings_goals:
            total = self.portfolio.get_total_balance_in(Currency.USD, self.exchange_service)
            if total.amount > 0:
                recommendations.append(Recommendation(
                    title="Set Savings Goals",
                    description="You have savings but no defined goals. "
                              "Setting clear savings goals helps you stay motivated and track progress.",
                    priority="medium"
                ))

        return recommendations

    def get_diversification_advice(self) -> List[Recommendation]:
        """Provide currency diversification recommendations."""
        recommendations = []

        balances = self.portfolio.get_balance_breakdown()
        total_usd = self.portfolio.get_total_balance_in(Currency.USD, self.exchange_service)

        if total_usd.amount > 1000:  # Only advise if significant savings
            currencies_with_balance = [c for c, b in balances.items() if b.amount > 0]

            if len(currencies_with_balance) == 1:
                recommendations.append(Recommendation(
                    title="Diversify Across Currencies",
                    description="All your savings are in one currency. Consider spreading across "
                              "2-3 stable currencies (e.g., USD, GBP) to hedge against exchange rate fluctuations.",
                    priority="medium"
                ))

            # Recommend stable currencies
            stable_currencies = [Currency.USD, Currency.GBP]
            has_stable = any(c in currencies_with_balance for c in stable_currencies)

            if not has_stable and total_usd.amount > 5000:
                recommendations.append(Recommendation(
                    title="Add Stable Currency Holdings",
                    description="Consider keeping a portion of your savings in stable currencies "
                              "like USD or GBP for long-term value preservation.",
                    priority="medium"
                ))

        return recommendations

    def get_all_recommendations(self) -> List[Recommendation]:
        """Get all recommendations sorted by priority."""
        all_recommendations = []

        all_recommendations.extend(self.get_goal_recommendations())
        all_recommendations.extend(self.get_currency_recommendations())
        all_recommendations.extend(self.get_diversification_advice())

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        all_recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))

        return all_recommendations

    def _identify_weak_currencies(self) -> List[Currency]:
        """Identify currencies that may be weakening (simplified logic)."""
        # In a real application, this would analyze historical trends
        # For now, we'll use a simple heuristic based on volatility
        weak = []

        # NGN is known to be more volatile
        rates = self.exchange_service.get_all_rates(Currency.USD)
        ngn_rate = rates.get(Currency.NGN, 0)

        if ngn_rate > 1500:  # High rate indicates weaker currency
            weak.append(Currency.NGN)

        return weak

    def calculate_optimal_allocation(self, total_amount: Money) -> Dict[Currency, Money]:
        """Calculate optimal currency allocation for a given amount."""
        # Simple allocation strategy: 40% USD, 30% GBP, 20% SAR, 10% NGN
        allocation = {
            Currency.USD: 0.40,
            Currency.GBP: 0.30,
            Currency.SAR: 0.20,
            Currency.NGN: 0.10,
        }

        result = {}
        for currency, percentage in allocation.items():
            allocated = self.exchange_service.convert(
                Money(total_amount.amount * percentage, total_amount.currency),
                currency
            )
            result[currency] = allocated

        return result
