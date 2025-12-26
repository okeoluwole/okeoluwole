"""Command-line interface for the Multi-Currency Savings Advisor."""

import sys
from datetime import date, timedelta
from typing import Optional
from tabulate import tabulate
from colorama import init, Fore, Style

from .models import Currency, Money, Portfolio, SavingsGoal
from .services import ExchangeRateService, SavingsAdvisor

# Initialize colorama
init(autoreset=True)


class SavingsAdvisorCLI:
    """Interactive CLI for the savings advisor."""

    def __init__(self):
        self.exchange_service = ExchangeRateService()
        self.portfolio = Portfolio(name="My Portfolio")
        self.running = True

    def print_header(self):
        """Print application header."""
        print(f"\n{Fore.CYAN}{'=' * 70}")
        print(f"{Fore.CYAN}{'  MULTI-CURRENCY SAVINGS ADVISOR':^70}")
        print(f"{Fore.CYAN}{'  Supporting SAR, USD, GBP, NGN':^70}")
        print(f"{Fore.CYAN}{'=' * 70}\n")

    def print_menu(self):
        """Print main menu."""
        print(f"\n{Fore.YELLOW}Main Menu:")
        print("1.  View Portfolio Summary")
        print("2.  View Currency Balances")
        print("3.  View Exchange Rates")
        print("4.  Deposit Money")
        print("5.  Withdraw Money")
        print("6.  Transfer Between Currencies")
        print("7.  View Savings Goals")
        print("8.  Create Savings Goal")
        print("9.  Contribute to Goal")
        print("10. Get Savings Recommendations")
        print("11. View Transaction History")
        print("12. Calculate Optimal Allocation")
        print("0.  Exit")
        print()

    def get_currency_choice(self, prompt: str = "Select currency") -> Optional[Currency]:
        """Get currency selection from user."""
        print(f"\n{prompt}:")
        for i, currency in enumerate(Currency, 1):
            print(f"{i}. {currency.value}")

        try:
            choice = int(input("Enter choice (1-4): "))
            currencies = list(Currency)
            if 1 <= choice <= len(currencies):
                return currencies[choice - 1]
        except (ValueError, IndexError):
            pass

        print(f"{Fore.RED}Invalid choice!")
        return None

    def get_amount(self, currency: Currency) -> Optional[Money]:
        """Get amount from user."""
        try:
            amount = float(input(f"Enter amount in {currency.value}: "))
            if amount < 0:
                print(f"{Fore.RED}Amount cannot be negative!")
                return None
            return Money(amount, currency)
        except ValueError:
            print(f"{Fore.RED}Invalid amount!")
            return None

    def view_portfolio_summary(self):
        """Display portfolio summary."""
        print(f"\n{Fore.CYAN}=== Portfolio Summary ===\n")

        advisor = SavingsAdvisor(self.portfolio, self.exchange_service)
        analysis = advisor.analyze_portfolio()

        print(f"Total Balance (USD): {Fore.GREEN}{analysis['total_balance_usd']}")
        print(f"Active Goals: {analysis['active_goals']}")
        print(f"Completed Goals: {analysis['completed_goals']}")
        print(f"Overdue Goals: {analysis['overdue_goals']}")

    def view_currency_balances(self):
        """Display currency balances."""
        print(f"\n{Fore.CYAN}=== Currency Balances ===\n")

        balances = self.portfolio.get_balance_breakdown()
        table_data = []

        for currency, balance in balances.items():
            balance_usd = self.exchange_service.convert(balance, Currency.USD)
            table_data.append([
                currency.value,
                f"{balance}",
                f"{balance_usd}"
            ])

        headers = ["Currency", "Balance", "USD Equivalent"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_exchange_rates(self):
        """Display current exchange rates."""
        print(f"\n{Fore.CYAN}=== Exchange Rates (Base: USD) ===\n")

        rates = self.exchange_service.get_all_rates(Currency.USD)
        is_live = self.exchange_service.is_rates_live()

        status = f"{Fore.GREEN}Live Rates" if is_live else f"{Fore.YELLOW}Fallback Rates"
        print(f"Status: {status}\n")

        table_data = []
        for currency, rate in rates.items():
            table_data.append([
                currency.value,
                f"{rate:.4f}",
                f"1 USD = {rate:.4f} {currency.value}"
            ])

        headers = ["Currency", "Rate", "Exchange"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def deposit_money(self):
        """Handle money deposit."""
        print(f"\n{Fore.CYAN}=== Deposit Money ===\n")

        currency = self.get_currency_choice("Select deposit currency")
        if not currency:
            return

        amount = self.get_amount(currency)
        if not amount:
            return

        description = input("Description (optional): ")
        self.portfolio.deposit(amount, description)

        print(f"{Fore.GREEN}Successfully deposited {amount}!")

    def withdraw_money(self):
        """Handle money withdrawal."""
        print(f"\n{Fore.CYAN}=== Withdraw Money ===\n")

        currency = self.get_currency_choice("Select withdrawal currency")
        if not currency:
            return

        account = self.portfolio.get_account(currency)
        print(f"Available balance: {account.balance}")

        amount = self.get_amount(currency)
        if not amount:
            return

        try:
            description = input("Description (optional): ")
            self.portfolio.withdraw(amount, description)
            print(f"{Fore.GREEN}Successfully withdrew {amount}!")
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}")

    def transfer_currencies(self):
        """Handle currency transfer/conversion."""
        print(f"\n{Fore.CYAN}=== Transfer Between Currencies ===\n")

        from_currency = self.get_currency_choice("Select source currency")
        if not from_currency:
            return

        from_account = self.portfolio.get_account(from_currency)
        print(f"Available balance: {from_account.balance}")

        amount = self.get_amount(from_currency)
        if not amount:
            return

        to_currency = self.get_currency_choice("Select destination currency")
        if not to_currency:
            return

        try:
            # Withdraw from source
            self.portfolio.withdraw(amount, f"Transfer to {to_currency.value}")

            # Convert and deposit to destination
            converted = self.exchange_service.convert(amount, to_currency)
            self.portfolio.deposit(converted, f"Transfer from {from_currency.value}")

            print(f"{Fore.GREEN}Successfully transferred {amount} to {converted}!")
            print(f"Exchange rate: 1 {from_currency.value} = "
                  f"{converted.amount / amount.amount:.4f} {to_currency.value}")
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}")

    def view_savings_goals(self):
        """Display all savings goals."""
        print(f"\n{Fore.CYAN}=== Savings Goals ===\n")

        if not self.portfolio.savings_goals:
            print("No savings goals yet. Create one to get started!")
            return

        for i, goal in enumerate(self.portfolio.savings_goals, 1):
            status_color = {
                "Completed": Fore.GREEN,
                "In Progress": Fore.YELLOW,
                "Overdue": Fore.RED,
                "Not Started": Fore.WHITE
            }.get(goal.status.value, Fore.WHITE)

            print(f"\n{Fore.CYAN}{i}. {goal.name}")
            print(f"   Status: {status_color}{goal.status.value}")
            print(f"   Target: {goal.target_amount}")
            print(f"   Current: {goal.current_amount}")
            print(f"   Progress: {goal.progress_percentage:.1f}%")
            print(f"   Remaining: {goal.remaining_amount}")

            if goal.deadline:
                print(f"   Deadline: {goal.deadline}")
                if goal.days_remaining is not None:
                    print(f"   Days Remaining: {goal.days_remaining}")

                daily = goal.daily_savings_needed()
                if daily:
                    print(f"   Daily Savings Needed: {daily}")

            if goal.description:
                print(f"   Description: {goal.description}")

    def create_savings_goal(self):
        """Create a new savings goal."""
        print(f"\n{Fore.CYAN}=== Create Savings Goal ===\n")

        name = input("Goal name: ")
        if not name:
            print(f"{Fore.RED}Goal name is required!")
            return

        currency = self.get_currency_choice("Select currency for goal")
        if not currency:
            return

        target_amount = self.get_amount(currency)
        if not target_amount:
            return

        description = input("Description (optional): ")

        has_deadline = input("Set deadline? (y/n): ").lower() == 'y'
        deadline = None

        if has_deadline:
            try:
                days = int(input("Days from now: "))
                deadline = date.today() + timedelta(days=days)
            except ValueError:
                print(f"{Fore.YELLOW}Invalid days, continuing without deadline...")

        goal = SavingsGoal(
            name=name,
            target_amount=target_amount,
            description=description,
            deadline=deadline
        )

        self.portfolio.add_savings_goal(goal)
        print(f"{Fore.GREEN}Successfully created savings goal '{name}'!")

    def contribute_to_goal(self):
        """Contribute to a savings goal."""
        print(f"\n{Fore.CYAN}=== Contribute to Goal ===\n")

        if not self.portfolio.savings_goals:
            print("No savings goals available!")
            return

        # List goals
        for i, goal in enumerate(self.portfolio.savings_goals, 1):
            print(f"{i}. {goal.name} - {goal.current_amount}/{goal.target_amount}")

        try:
            choice = int(input("\nSelect goal (number): "))
            if 1 <= choice <= len(self.portfolio.savings_goals):
                goal = self.portfolio.savings_goals[choice - 1]

                amount = self.get_amount(goal.target_amount.currency)
                if not amount:
                    return

                account = self.portfolio.get_account(amount.currency)
                if amount.amount > account.balance.amount:
                    print(f"{Fore.RED}Insufficient funds in {amount.currency.value} account!")
                    return

                self.portfolio.contribute_to_goal(goal.name, amount)
                print(f"{Fore.GREEN}Successfully contributed {amount} to '{goal.name}'!")
                print(f"New progress: {goal.progress_percentage:.1f}%")

            else:
                print(f"{Fore.RED}Invalid choice!")
        except ValueError:
            print(f"{Fore.RED}Invalid input!")

    def get_recommendations(self):
        """Display savings recommendations."""
        print(f"\n{Fore.CYAN}=== Savings Recommendations ===\n")

        advisor = SavingsAdvisor(self.portfolio, self.exchange_service)
        recommendations = advisor.get_all_recommendations()

        if not recommendations:
            print(f"{Fore.GREEN}Great job! No urgent recommendations at this time.")
            return

        for i, rec in enumerate(recommendations, 1):
            priority_color = {
                "high": Fore.RED,
                "medium": Fore.YELLOW,
                "low": Fore.WHITE
            }.get(rec.priority, Fore.WHITE)

            print(f"{i}. {priority_color}[{rec.priority.upper()}] {rec.title}")
            print(f"   {rec.description}")
            if rec.savings_impact:
                print(f"   Impact: {rec.savings_impact}")
            print()

    def view_transaction_history(self):
        """Display transaction history."""
        print(f"\n{Fore.CYAN}=== Transaction History ===\n")

        transactions = self.portfolio.get_all_transactions()

        if not transactions:
            print("No transactions yet!")
            return

        table_data = []
        for trans in transactions[:20]:  # Show last 20
            table_data.append([
                trans.timestamp.strftime("%Y-%m-%d %H:%M"),
                trans.transaction_type.capitalize(),
                str(trans.amount),
                trans.description[:40] if trans.description else "-"
            ])

        headers = ["Date/Time", "Type", "Amount", "Description"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        if len(transactions) > 20:
            print(f"\n{Fore.YELLOW}Showing last 20 of {len(transactions)} transactions")

    def calculate_allocation(self):
        """Calculate optimal currency allocation."""
        print(f"\n{Fore.CYAN}=== Calculate Optimal Allocation ===\n")

        currency = self.get_currency_choice("Select currency for allocation calculation")
        if not currency:
            return

        amount = self.get_amount(currency)
        if not amount:
            return

        advisor = SavingsAdvisor(self.portfolio, self.exchange_service)
        allocation = advisor.calculate_optimal_allocation(amount)

        print(f"\n{Fore.CYAN}Recommended allocation for {amount}:\n")

        table_data = []
        for curr, allocated in allocation.items():
            percentage = (allocated.amount / sum(a.amount for a in allocation.values())) * 100
            table_data.append([
                curr.value,
                f"{allocated}",
                f"{percentage:.1f}%"
            ])

        headers = ["Currency", "Amount", "Percentage"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def run(self):
        """Run the CLI application."""
        self.print_header()

        # Fetch exchange rates
        print("Fetching exchange rates...")
        self.exchange_service.fetch_rates()

        while self.running:
            self.print_menu()

            try:
                choice = input("Enter your choice: ")

                if choice == "0":
                    print(f"\n{Fore.CYAN}Thank you for using Multi-Currency Savings Advisor!")
                    self.running = False
                elif choice == "1":
                    self.view_portfolio_summary()
                elif choice == "2":
                    self.view_currency_balances()
                elif choice == "3":
                    self.view_exchange_rates()
                elif choice == "4":
                    self.deposit_money()
                elif choice == "5":
                    self.withdraw_money()
                elif choice == "6":
                    self.transfer_currencies()
                elif choice == "7":
                    self.view_savings_goals()
                elif choice == "8":
                    self.create_savings_goal()
                elif choice == "9":
                    self.contribute_to_goal()
                elif choice == "10":
                    self.get_recommendations()
                elif choice == "11":
                    self.view_transaction_history()
                elif choice == "12":
                    self.calculate_allocation()
                else:
                    print(f"{Fore.RED}Invalid choice! Please try again.")

            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}Exiting...")
                self.running = False
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
                print(f"{Fore.YELLOW}Please try again.")


def main():
    """Main entry point."""
    cli = SavingsAdvisorCLI()
    cli.run()


if __name__ == "__main__":
    main()
