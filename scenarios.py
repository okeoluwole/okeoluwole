#!/usr/bin/env python3
"""
Real-world savings scenarios for the Multi-Currency Savings Advisor.
"""

from datetime import date, timedelta
from src.models import Currency, Money, Portfolio, SavingsGoal
from src.services import ExchangeRateService, SavingsAdvisor
from tabulate import tabulate
from colorama import init, Fore, Style

init(autoreset=True)


def divider(title=""):
    print(f"\n{Fore.CYAN}{'─' * 70}")
    if title:
        print(f"{Fore.CYAN}  {title}")
        print(f"{Fore.CYAN}{'─' * 70}")


def section(title):
    print(f"\n{Fore.YELLOW}{'=' * 70}")
    print(f"{Fore.YELLOW}  {title}")
    print(f"{Fore.YELLOW}{'=' * 70}\n")


def show_portfolio(portfolio, exchange_service, label=""):
    if label:
        print(f"\n{Fore.CYAN}{label}:")
    rows = []
    for currency, account in portfolio.accounts.items():
        if account.balance.amount > 0:
            usd = exchange_service.convert(account.balance, Currency.USD)
            rows.append([currency.value, str(account.balance), str(usd)])
    total = portfolio.get_total_balance_in(Currency.USD, exchange_service)
    print(tabulate(rows, headers=["Currency", "Balance", "≈ USD"], tablefmt="simple"))
    print(f"  {Fore.GREEN}Total: {total}")


def show_goals(portfolio):
    for goal in portfolio.savings_goals:
        bar_filled = int(goal.progress_percentage / 5)
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        color = Fore.GREEN if goal.progress_percentage >= 100 else Fore.YELLOW if goal.progress_percentage >= 50 else Fore.WHITE
        print(f"  {color}{goal.name:<25} [{bar}] {goal.progress_percentage:5.1f}%  ({goal.current_amount} / {goal.target_amount})")


def show_recommendations(portfolio, exchange_service):
    advisor = SavingsAdvisor(portfolio, exchange_service)
    recs = advisor.get_all_recommendations()
    if not recs:
        print(f"  {Fore.GREEN}No urgent recommendations — portfolio looks healthy!")
        return
    for rec in recs:
        color = Fore.RED if rec.priority == "high" else Fore.YELLOW if rec.priority == "medium" else Fore.WHITE
        print(f"  {color}[{rec.priority.upper()}] {rec.title}")
        print(f"         {rec.description}")
        if rec.savings_impact:
            print(f"         Save {rec.savings_impact} per day to stay on track.")


# ─── Setup ────────────────────────────────────────────────────────────────────
exchange_service = ExchangeRateService()
exchange_service.fetch_rates()


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 1: Nigerian Student Saving to Study in the UK
# ══════════════════════════════════════════════════════════════════════════════
section("SCENARIO 1 — Nigerian Student Saving to Study in the UK")
print("Amaka earns ₦450,000/month and wants to study at the University of")
print("London. She needs £18,000 for tuition + £6,000 living costs = £24,000.")
print("She has 18 months to save and currently holds some USD as a buffer.\n")

amaka = Portfolio(name="Amaka")
amaka.deposit(Money(1_200_000, Currency.NGN), "Savings from last year")
amaka.deposit(Money(800,       Currency.USD), "Emergency buffer")

divider("Initial Portfolio")
show_portfolio(amaka, exchange_service)

# Goals
amaka.add_savings_goal(SavingsGoal(
    name="Tuition Fee",
    target_amount=Money(18_000, Currency.GBP),
    deadline=date.today() + timedelta(days=540),
    description="University of London tuition"
))
amaka.add_savings_goal(SavingsGoal(
    name="Living Costs",
    target_amount=Money(6_000, Currency.GBP),
    deadline=date.today() + timedelta(days=540),
    description="First year accommodation & food"
))

# Monthly saving simulation — 6 months
print(f"\n{Fore.CYAN}Simulating 6 months of saving (₦150,000 GBP savings/month)...")
for month in range(1, 7):
    amaka.deposit(Money(150_000, Currency.NGN), f"Month {month} salary savings")
    converted = exchange_service.convert(Money(150_000, Currency.NGN), Currency.GBP)
    amaka.withdraw(Money(150_000, Currency.NGN), f"Convert to GBP month {month}")
    amaka.deposit(converted, f"GBP savings month {month}")

    # Contribute 75% to tuition, then use exact remaining balance for living costs
    gbp_balance = amaka.get_account(Currency.GBP).balance.amount
    tuition_amt = round(gbp_balance * 0.75, 2)
    amaka.contribute_to_goal("Tuition Fee", Money(tuition_amt, Currency.GBP))
    # Read balance again after first withdrawal to get the precise remainder
    living_amt = amaka.get_account(Currency.GBP).balance.amount
    amaka.contribute_to_goal("Living Costs", Money(living_amt, Currency.GBP))

divider("After 6 Months of Saving")
show_portfolio(amaka, exchange_service)
print()
show_goals(amaka)

divider("Advisor Recommendations")
show_recommendations(amaka, exchange_service)


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 2: Saudi Expat Worker Building a Multi-Currency Safety Net
# ══════════════════════════════════════════════════════════════════════════════
section("SCENARIO 2 — Saudi Expat Worker with Multi-Currency Safety Net")
print("Khalid works in Riyadh and earns ﷼15,000/month. He sends money home")
print("to Nigeria (NGN) and also saves in USD for stability. He wants to")
print("build an emergency fund and save for a car purchase.\n")

khalid = Portfolio(name="Khalid")
khalid.deposit(Money(45_000, Currency.SAR), "3 months salary saved")

divider("Initial Portfolio")
show_portfolio(khalid, exchange_service)

khalid.add_savings_goal(SavingsGoal(
    name="Emergency Fund",
    target_amount=Money(20_000, Currency.SAR),
    deadline=date.today() + timedelta(days=270),
    description="9 months of expenses"
))
khalid.add_savings_goal(SavingsGoal(
    name="Car Purchase",
    target_amount=Money(60_000, Currency.SAR),
    deadline=date.today() + timedelta(days=365),
    description="Toyota Camry"
))
khalid.add_savings_goal(SavingsGoal(
    name="Family Remittance Fund",
    target_amount=Money(2_000_000, Currency.NGN),
    deadline=date.today() + timedelta(days=180),
    description="Send money home"
))

# Remittance: convert SAR → NGN
remittance_sar = Money(5_000, Currency.SAR)
khalid.withdraw(remittance_sar, "Convert for family remittance")
remittance_ngn = exchange_service.convert(remittance_sar, Currency.NGN)
khalid.deposit(remittance_ngn, "NGN family fund")
khalid.contribute_to_goal("Family Remittance Fund", Money(min(remittance_ngn.amount, 2_000_000), Currency.NGN))

# Emergency + car contributions
khalid.contribute_to_goal("Emergency Fund", Money(15_000, Currency.SAR))
khalid.contribute_to_goal("Car Purchase",   Money(20_000, Currency.SAR))

divider("Portfolio After Contributions")
show_portfolio(khalid, exchange_service)
print()
show_goals(khalid)

divider("Advisor Recommendations")
show_recommendations(khalid, exchange_service)


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 3: UK Professional Diversifying Into SAR & NGN
# ══════════════════════════════════════════════════════════════════════════════
section("SCENARIO 3 — UK Professional Diversifying Across 4 Currencies")
print("James is a London-based software engineer earning £6,500/month.")
print("He wants to diversify savings across currencies and is planning a")
print("sabbatical trip to Saudi Arabia and Nigeria in 2 years.\n")

james = Portfolio(name="James")
james.deposit(Money(15_000, Currency.GBP), "Current savings")
james.deposit(Money(5_000,  Currency.USD), "US tech contract payment")

divider("Initial Portfolio")
show_portfolio(james, exchange_service)

james.add_savings_goal(SavingsGoal(
    name="Sabbatical Fund",
    target_amount=Money(20_000, Currency.GBP),
    deadline=date.today() + timedelta(days=730),
    description="24-month sabbatical travel fund"
))
james.add_savings_goal(SavingsGoal(
    name="House Deposit",
    target_amount=Money(50_000, Currency.GBP),
    deadline=date.today() + timedelta(days=1095),
    description="London property down payment"
))

# Diversify into SAR and NGN
print(f"\n{Fore.CYAN}Diversifying into SAR and NGN...")
james.withdraw(Money(2_000, Currency.GBP), "Diversify to SAR")
sar_amount = exchange_service.convert(Money(2_000, Currency.GBP), Currency.SAR)
james.deposit(sar_amount, "GBP → SAR diversification")
print(f"  £2,000 GBP → {sar_amount}")

james.withdraw(Money(1_000, Currency.USD), "Diversify to NGN")
ngn_amount = exchange_service.convert(Money(1_000, Currency.USD), Currency.NGN)
james.deposit(ngn_amount, "USD → NGN diversification")
print(f"  $1,000 USD → {ngn_amount}")

# Monthly contributions
for month in range(1, 7):
    james.deposit(Money(2_000, Currency.GBP), f"Month {month} savings")
    james.contribute_to_goal("Sabbatical Fund",  Money(1_200, Currency.GBP))
    james.contribute_to_goal("House Deposit",    Money(800,   Currency.GBP))

divider("Portfolio After Diversification + 6 Months")
show_portfolio(james, exchange_service)
print()
show_goals(james)

divider("Advisor Recommendations")
show_recommendations(james, exchange_service)


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO 4: Overdue Goal — What Happens When You Fall Behind
# ══════════════════════════════════════════════════════════════════════════════
section("SCENARIO 4 — Overdue Goal & Recovery Plan")
print("Bola set a savings goal 6 months ago but has barely contributed.")
print("See how the advisor flags overdue goals and suggests a recovery plan.\n")

bola = Portfolio(name="Bola")
bola.deposit(Money(800_000, Currency.NGN), "Current balance")

bola.add_savings_goal(SavingsGoal(
    name="New Laptop",
    target_amount=Money(500_000, Currency.NGN),
    deadline=date.today() - timedelta(days=10),   # already overdue!
    description="MacBook Pro for freelancing"
))
bola.add_savings_goal(SavingsGoal(
    name="Business Capital",
    target_amount=Money(2_000_000, Currency.NGN),
    deadline=date.today() + timedelta(days=25),   # nearly out of time!
    description="Start online business"
))

bola.contribute_to_goal("New Laptop",       Money(100_000, Currency.NGN))
bola.contribute_to_goal("Business Capital", Money(400_000, Currency.NGN))

divider("Bola's Current Portfolio")
show_portfolio(bola, exchange_service)
print()
show_goals(bola)

divider("Advisor Flags — High Priority Alerts")
show_recommendations(bola, exchange_service)


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ══════════════════════════════════════════════════════════════════════════════
section("SUMMARY — All Scenario Portfolios in USD")

rows = []
for name, portfolio in [("Amaka (Student)", amaka), ("Khalid (Expat)", khalid),
                         ("James (UK Pro)", james), ("Bola (Behind)", bola)]:
    total = portfolio.get_total_balance_in(Currency.USD, exchange_service)
    goals = len(portfolio.savings_goals)
    rows.append([name, str(total), goals])

print(tabulate(rows, headers=["Person", "Total Portfolio (USD)", "Goals"], tablefmt="grid"))
print(f"\n{Fore.GREEN}All 4 scenarios completed successfully!")
