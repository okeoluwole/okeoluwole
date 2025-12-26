#!/usr/bin/env python3
"""
Demo script to showcase the Multi-Currency Savings Advisor features.
This demonstrates the core functionality without the interactive CLI.
"""

from datetime import date, timedelta
from src.models import Currency, Money, Portfolio, SavingsGoal
from src.services import ExchangeRateService, SavingsAdvisor
from tabulate import tabulate
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


def print_section(title):
    """Print a section header."""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}{title:^70}")
    print(f"{Fore.CYAN}{'=' * 70}\n")


def main():
    """Run the demo."""
    print_section("MULTI-CURRENCY SAVINGS ADVISOR DEMO")

    # Initialize services
    print(f"{Fore.YELLOW}Initializing services...")
    exchange_service = ExchangeRateService()
    portfolio = Portfolio(name="Demo Portfolio")

    print(f"{Fore.GREEN}✓ Services initialized")

    # Fetch exchange rates
    print_section("1. EXCHANGE RATES")
    print(f"{Fore.YELLOW}Fetching live exchange rates...")
    exchange_service.fetch_rates()
    is_live = exchange_service.is_rates_live()
    status = f"{Fore.GREEN}Live" if is_live else f"{Fore.YELLOW}Fallback"
    print(f"Status: {status} rates\n")

    rates = exchange_service.get_all_rates(Currency.USD)
    table_data = []
    for currency, rate in rates.items():
        table_data.append([
            currency.value,
            f"{rate:.4f}",
            f"1 USD = {rate:.4f} {currency.value}"
        ])
    print(tabulate(table_data, headers=["Currency", "Rate", "Exchange"], tablefmt="grid"))

    # Deposit money
    print_section("2. DEPOSITING MONEY")
    deposits = [
        Money(5000, Currency.SAR),
        Money(2000, Currency.USD),
        Money(1500, Currency.GBP),
        Money(500000, Currency.NGN),
    ]

    for amount in deposits:
        portfolio.deposit(amount, "Initial deposit")
        print(f"{Fore.GREEN}✓ Deposited {amount}")

    # View balances
    print_section("3. PORTFOLIO BALANCES")
    balances = portfolio.get_balance_breakdown()
    table_data = []
    for currency, balance in balances.items():
        balance_usd = exchange_service.convert(balance, Currency.USD)
        table_data.append([
            currency.value,
            str(balance),
            str(balance_usd)
        ])
    print(tabulate(table_data, headers=["Currency", "Balance", "USD Equivalent"], tablefmt="grid"))

    total_usd = portfolio.get_total_balance_in(Currency.USD, exchange_service)
    print(f"\n{Fore.GREEN}Total Portfolio Value: {total_usd}")

    # Currency conversion
    print_section("4. CURRENCY CONVERSION")
    convert_amount = Money(1000, Currency.SAR)
    print(f"Converting {convert_amount} to USD...")

    # Withdraw from SAR
    portfolio.withdraw(convert_amount, "Transfer to USD")
    converted = exchange_service.convert(convert_amount, Currency.USD)
    portfolio.deposit(converted, "Transfer from SAR")

    rate = converted.amount / convert_amount.amount
    print(f"{Fore.GREEN}✓ Converted {convert_amount} → {converted}")
    print(f"  Exchange rate: 1 SAR = {rate:.4f} USD")

    # Create savings goals
    print_section("5. CREATING SAVINGS GOALS")

    goals = [
        SavingsGoal(
            name="Emergency Fund",
            target_amount=Money(5000, Currency.USD),
            deadline=date.today() + timedelta(days=180),
            description="6 months of expenses"
        ),
        SavingsGoal(
            name="Vacation to London",
            target_amount=Money(3000, Currency.GBP),
            deadline=date.today() + timedelta(days=90),
            description="Summer vacation"
        ),
        SavingsGoal(
            name="Hajj Savings",
            target_amount=Money(30000, Currency.SAR),
            deadline=date.today() + timedelta(days=365),
            description="Save for Hajj pilgrimage"
        ),
    ]

    for goal in goals:
        portfolio.add_savings_goal(goal)
        daily = goal.daily_savings_needed()
        print(f"{Fore.GREEN}✓ Created goal: {goal.name}")
        print(f"  Target: {goal.target_amount}")
        print(f"  Deadline: {goal.deadline} ({goal.days_remaining} days)")
        if daily:
            print(f"  Daily savings needed: {daily}")

    # Contribute to goals
    print_section("6. CONTRIBUTING TO GOALS")

    contributions = [
        ("Emergency Fund", Money(1000, Currency.USD)),
        ("Vacation to London", Money(500, Currency.GBP)),
        ("Hajj Savings", Money(2000, Currency.SAR)),
    ]

    for goal_name, amount in contributions:
        portfolio.contribute_to_goal(goal_name, amount)
        goal = portfolio.get_savings_goal(goal_name)
        print(f"{Fore.GREEN}✓ Contributed {amount} to '{goal_name}'")
        print(f"  Progress: {goal.progress_percentage:.1f}%")
        print(f"  Current: {goal.current_amount}/{goal.target_amount}")

    # View goals
    print_section("7. SAVINGS GOALS STATUS")

    for i, goal in enumerate(portfolio.savings_goals, 1):
        status_color = {
            "Completed": Fore.GREEN,
            "In Progress": Fore.YELLOW,
            "Overdue": Fore.RED,
            "Not Started": Fore.WHITE
        }.get(goal.status.value, Fore.WHITE)

        print(f"\n{Fore.CYAN}{i}. {goal.name}")
        print(f"   Status: {status_color}{goal.status.value}")
        print(f"   Progress: {goal.progress_percentage:.1f}%")
        print(f"   Current: {goal.current_amount}")
        print(f"   Target: {goal.target_amount}")
        print(f"   Remaining: {goal.remaining_amount}")
        if goal.days_remaining:
            print(f"   Days remaining: {goal.days_remaining}")
            daily = goal.daily_savings_needed()
            if daily:
                print(f"   Daily savings needed: {daily}")

    # Get recommendations
    print_section("8. SAVINGS RECOMMENDATIONS")

    advisor = SavingsAdvisor(portfolio, exchange_service)
    recommendations = advisor.get_all_recommendations()

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            priority_color = {
                "high": Fore.RED,
                "medium": Fore.YELLOW,
                "low": Fore.WHITE
            }.get(rec.priority, Fore.WHITE)

            print(f"{i}. {priority_color}[{rec.priority.upper()}] {rec.title}")
            print(f"   {rec.description}")
            if rec.savings_impact:
                print(f"   Daily savings needed: {rec.savings_impact}")
            print()
    else:
        print(f"{Fore.GREEN}Great job! No urgent recommendations.")

    # Portfolio analysis
    print_section("9. PORTFOLIO ANALYSIS")

    analysis = advisor.analyze_portfolio()
    print(f"Total Balance (USD): {Fore.GREEN}{analysis['total_balance_usd']}")
    print(f"Active Goals: {analysis['active_goals']}")
    print(f"Completed Goals: {analysis['completed_goals']}")
    print(f"Overdue Goals: {analysis['overdue_goals']}")

    # Optimal allocation
    print_section("10. OPTIMAL ALLOCATION")

    test_amount = Money(10000, Currency.USD)
    print(f"Calculating optimal allocation for {test_amount}...\n")

    allocation = advisor.calculate_optimal_allocation(test_amount)
    table_data = []
    for currency, amount in allocation.items():
        percentage = (amount.amount / sum(a.amount for a in allocation.values())) * 100
        table_data.append([
            currency.value,
            str(amount),
            f"{percentage:.1f}%"
        ])
    print(tabulate(table_data, headers=["Currency", "Amount", "Percentage"], tablefmt="grid"))

    # Transaction history
    print_section("11. TRANSACTION HISTORY")

    transactions = portfolio.get_all_transactions()
    print(f"Total transactions: {len(transactions)}\n")

    table_data = []
    for trans in transactions[:10]:  # Show last 10
        table_data.append([
            trans.timestamp.strftime("%H:%M:%S"),
            trans.transaction_type.capitalize(),
            str(trans.amount),
            trans.description[:35] + "..." if len(trans.description) > 35 else trans.description
        ])
    print(tabulate(table_data, headers=["Time", "Type", "Amount", "Description"], tablefmt="grid"))

    if len(transactions) > 10:
        print(f"\n{Fore.YELLOW}Showing last 10 of {len(transactions)} transactions")

    # Summary
    print_section("DEMO COMPLETE")
    print(f"{Fore.GREEN}✓ All features demonstrated successfully!")
    print(f"\nTo run the interactive CLI, use: {Fore.CYAN}python main.py")


if __name__ == "__main__":
    main()
