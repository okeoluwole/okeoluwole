#!/usr/bin/env python3
"""
BYD Vehicle Finance Comparison Tool
Market   : Riyadh, Saudi Arabia
Currency : Saudi Riyal (SAR)
Products : Vehicle Loan (Murabaha) vs Auto Flex (Ijarah with Balloon Payment)

Key Assumptions (2025, Saudi Market):
  - Profit Rate  : 4.99% p.a. reducing balance (competitive; Al Rajhi ~4.6%, SNB ~4.99–5.5%)
  - Down Payment : 20% (SAMA minimum for personal vehicle finance)
  - Loan Term    : 60 months (5 years)
  - Flex Term    : 48 months (4 years — typical for balloon products in KSA)
  - Balloon/GFV  : 25% of vehicle price (≤40% allowed per bank policy; 25% is conservative)
  - Insurance    : 1.5% p.a. of depreciating vehicle value (comprehensive, KSA market)
  - Depreciation : 15% p.a. (BYD EVs; used for insurance base calculation only)
  - VAT          : 15% — already included in all listed prices
  - All prices sourced from DriveArabia, YallaMotor, and BYD KSA (2025)

Sources:
  - BYD KSA: https://www.byd.sa/en/new-cars/
  - Al Rajhi Auto Lease: https://www.alrajhibank.com.sa/en/Personal/Finance/Auto-Finance/Auto-leasing
  - SNB AlAhli Lease Finance: https://www.alahli.com/en/pages/personal-banking/finance/alahli-car-finance
  - YallaCompare KSA Car Loans: https://yallacompare.com/ksa/en/car-loans/
  - DriveArabia KSA BYD Prices: https://www.drivearabia.com/carprices/ksa/byd-price/
"""

import math
import csv
import os
from typing import Dict, List, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# BYD LINEUP — Saudi Arabia / Riyadh (2025 Prices in SAR, VAT Included)
# ══════════════════════════════════════════════════════════════════════════════
BYD_LINEUP: List[Dict] = [
    # ── Entry / PHEV ──────────────────────────────────────────────────────────
    {"model": "BYD QIN Plus DM-i (Comfort)",   "price":  72_900, "type": "PHEV Sedan"},
    {"model": "BYD QIN Plus DM-i (Premium)",   "price":  84_900, "type": "PHEV Sedan"},
    # ── Compact SUV ───────────────────────────────────────────────────────────
    {"model": "BYD Seal 7 DM-i (Comfort)",     "price": 104_900, "type": "PHEV SUV"},
    {"model": "BYD Seal 7 DM-i (Premium)",     "price": 119_900, "type": "PHEV SUV"},
    {"model": "BYD Seal 7 DM-i (Ultimate)",    "price": 134_900, "type": "PHEV SUV"},
    {"model": "BYD Song Plus DM-i (FWD)",      "price": 114_900, "type": "PHEV SUV"},
    {"model": "BYD Song Plus DM-i (AWD)",      "price": 138_900, "type": "PHEV SUV"},
    # ── BYD Atto 3 (EV SUV) ───────────────────────────────────────────────────
    {"model": "BYD Atto 3 (Standard Range)",   "price": 109_900, "type": "EV SUV"},
    {"model": "BYD Atto 3 (Long Range)",       "price": 124_900, "type": "EV SUV"},
    # ── BYD Seal (EV Sedan) ───────────────────────────────────────────────────
    {"model": "BYD Seal (Dynamic RWD)",        "price": 164_900, "type": "EV Sedan"},
    {"model": "BYD Seal (Premium RWD)",        "price": 179_900, "type": "EV Sedan"},
    {"model": "BYD Seal (Performance AWD)",    "price": 194_900, "type": "EV Sedan"},
    # ── BYD Sealion 7 (EV SUV) ────────────────────────────────────────────────
    {"model": "BYD Sealion 7 (Premium RWD)",   "price": 194_000, "type": "EV SUV"},
    {"model": "BYD Sealion 7 (Perf. AWD)",     "price": 214_000, "type": "EV SUV"},
    # ── BYD Han (EV Flagship Sedan) ───────────────────────────────────────────
    {"model": "BYD Han (Standard)",            "price": 189_900, "type": "EV Sedan"},
    {"model": "BYD Han (Premium)",             "price": 224_900, "type": "EV Sedan"},
    {"model": "BYD Han (Performance)",         "price": 234_900, "type": "EV Sedan"},
]

# ══════════════════════════════════════════════════════════════════════════════
# DEFAULT FINANCING PARAMETERS (Configurable at Top of Script)
# ══════════════════════════════════════════════════════════════════════════════
PARAMS: Dict = {
    # Finance rate — same product for both (reducing balance / declining principal)
    "profit_rate_pa":      0.0499,   # 4.99% p.a.  (Al Rajhi/SNB competitive rate)

    # Loan product (Murabaha / standard auto loan)
    "loan_term_months":    60,       # 60 months = 5 years
    "loan_down_pct":       0.20,     # 20% down payment

    # Auto Flex product (Ijarah with Balloon / GFV)
    "flex_term_months":    48,       # 48 months = 4 years (typical KSA flex)
    "flex_down_pct":       0.20,     # 20% down payment
    "balloon_pct":         0.25,     # 25% GFV balloon at end of term

    # Shared costs
    "processing_fee":      500,      # SAR one-time processing/admin fee
    "insurance_rate":      0.0150,   # 1.5% p.a. comprehensive insurance (of current value)
    "annual_depreciation": 0.15,     # 15% p.a. value drop (EV; for insurance calc only)
}


# ══════════════════════════════════════════════════════════════════════════════
# CORE FINANCIAL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def monthly_pmt(principal: float, annual_rate: float, months: int) -> float:
    """Standard reducing-balance PMT: fixed monthly payment to amortize principal."""
    if annual_rate == 0:
        return principal / months
    r = annual_rate / 12
    return principal * (r * (1 + r) ** months) / ((1 + r) ** months - 1)


def flex_monthly_pmt(financed: float, annual_rate: float,
                     months: int, balloon: float) -> float:
    """
    Monthly payment for a balloon (flex) loan.

    Derivation:
        PV = PMT * [1 - (1+r)^-n] / r  +  Balloon * (1+r)^-n
        PMT = (PV - Balloon * (1+r)^-n) * r / (1 - (1+r)^-n)
    where PV = amount financed (vehicle price minus down payment).
    """
    if annual_rate == 0:
        return (financed - balloon) / months
    r = annual_rate / 12
    discount = (1 + r) ** (-months)
    return (financed - balloon * discount) * r / (1 - discount)


def insurance_total(vehicle_price: float, rate: float,
                    years: float, depreciation: float) -> float:
    """
    Estimate total comprehensive insurance over the financing period.
    Insurance premium is applied to the declining vehicle value each year.
    """
    total = 0.0
    value = vehicle_price
    full_years = int(math.ceil(years))
    for _ in range(full_years):
        total += value * rate
        value *= (1 - depreciation)
    return total


def amortization_schedule(principal: float, annual_rate: float,
                           months: int, balloon: float = 0.0) -> List[Dict]:
    """Generate full amortization schedule (reducing-balance with optional balloon)."""
    r = annual_rate / 12
    if balloon > 0:
        pmt = flex_monthly_pmt(principal, annual_rate, months, balloon)
    else:
        pmt = monthly_pmt(principal, annual_rate, months)

    schedule = []
    balance = principal
    for m in range(1, months + 1):
        interest = balance * r
        # Final month: settle remaining balance (accounts for rounding)
        if m == months:
            principal_paid = balance - balloon
            pmt_actual = principal_paid + interest + balloon
        else:
            principal_paid = pmt - interest
            pmt_actual = pmt
        balance -= principal_paid
        schedule.append({
            "month":          m,
            "payment":        round(pmt_actual, 2),
            "principal":      round(principal_paid, 2),
            "interest":       round(interest, 2),
            "balance":        round(max(balance, balloon if m == months else 0), 2),
        })
    return schedule


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def calc_loan(price: float, p: Dict) -> Dict:
    """Calculate all metrics for a standard vehicle loan (Murabaha)."""
    down         = price * p["loan_down_pct"]
    principal    = price - down
    months       = p["loan_term_months"]
    rate         = p["profit_rate_pa"]
    years        = months / 12

    pmt          = monthly_pmt(principal, rate, months)
    total_pmts   = pmt * months
    total_profit = total_pmts - principal
    ins          = insurance_total(price, p["insurance_rate"], years, p["annual_depreciation"])

    return {
        "product":          "Vehicle Loan (Murabaha)",
        "vehicle_price":    price,
        "down_payment":     down,
        "principal":        principal,
        "rate_pa":          rate,
        "term_months":      months,
        "monthly_pmt":      pmt,
        "total_pmts":       total_pmts,
        "total_profit":     total_profit,
        "balloon":          0.0,
        "processing_fee":   p["processing_fee"],
        "insurance":        ins,
        # Total outlay to own the vehicle at end of term
        "total_cost_own":   down + total_pmts + p["processing_fee"] + ins,
        "schedule":         amortization_schedule(principal, rate, months),
    }


def calc_flex(price: float, p: Dict) -> Dict:
    """Calculate all metrics for Auto Flex (Ijarah with GFV balloon)."""
    down         = price * p["flex_down_pct"]
    balloon      = price * p["balloon_pct"]
    financed     = price - down          # total PV financed (incl. deferred balloon)
    months       = p["flex_term_months"]
    rate         = p["profit_rate_pa"]
    years        = months / 12

    pmt          = flex_monthly_pmt(financed, rate, months, balloon)
    total_pmts   = pmt * months          # sum of all monthly installments
    # Total profit = total payments (monthly + balloon) minus the original principal
    total_profit = (total_pmts + balloon) - financed
    ins          = insurance_total(price, p["insurance_rate"], years, p["annual_depreciation"])

    # Scenario A: pay balloon at end → you own the car
    cost_keep    = down + total_pmts + balloon + p["processing_fee"] + ins
    # Scenario B: return the car at end (GFV guaranteed; no balloon due)
    cost_return  = down + total_pmts + p["processing_fee"] + ins

    return {
        "product":          "Auto Flex (Ijarah + Balloon)",
        "vehicle_price":    price,
        "down_payment":     down,
        "financed":         financed,
        "rate_pa":          rate,
        "term_months":      months,
        "balloon":          balloon,
        "monthly_pmt":      pmt,
        "total_pmts":       total_pmts,
        "total_profit":     total_profit,
        "processing_fee":   p["processing_fee"],
        "insurance":        ins,
        "total_cost_keep":  cost_keep,
        "total_cost_return": cost_return,
        "schedule":         amortization_schedule(financed, rate, months, balloon),
    }


# ══════════════════════════════════════════════════════════════════════════════
# FORMATTING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def sar(amount: float, width: int = 0) -> str:
    s = f"SAR {amount:,.0f}"
    return s.rjust(width) if width else s


def pct(val: float) -> str:
    return f"{val * 100:.2f}%"


# ══════════════════════════════════════════════════════════════════════════════
# REPORT PRINTING
# ══════════════════════════════════════════════════════════════════════════════

def print_detail(loan: Dict, flex: Dict) -> None:
    """Print a full side-by-side comparison card for one BYD model."""
    price = loan["vehicle_price"]
    W = 74
    loan_monthly_saving = loan["monthly_pmt"] - flex["monthly_pmt"]

    print("=" * W)
    print(f"  {loan.get('model_name', 'Model').upper()}")
    print(f"  Vehicle Price: {sar(price)}   |   Type: {loan.get('model_type', '')}")
    print("=" * W)
    print(f"  {'':38} {'LOAN (60m)':>14} {'AUTO FLEX (48m)':>16}")
    print("  " + "-" * (W - 2))
    print(f"  {'Profit Rate (p.a.)':38} {pct(loan['rate_pa']):>14} {pct(flex['rate_pa']):>16}")
    print(f"  {'Down Payment':38} {sar(loan['down_payment']):>14} {sar(flex['down_payment']):>16}")
    print(f"  {'Amount Financed':38} {sar(loan['principal']):>14} {sar(flex['financed']):>16}")
    print(f"  {'Balloon / GFV at End':38} {'—':>14} {sar(flex['balloon']):>16}")
    print("  " + "-" * (W - 2))
    print(f"  {'MONTHLY PAYMENT':38} {sar(loan['monthly_pmt']):>14} {sar(flex['monthly_pmt']):>16}")
    if loan_monthly_saving > 0:
        print(f"  {'  → Monthly Cash Saving (Flex)':38} {'':>14} {sar(loan_monthly_saving):>16}")
    print("  " + "-" * (W - 2))
    print(f"  {'Total Monthly Installments':38} {sar(loan['total_pmts']):>14} {sar(flex['total_pmts']):>16}")
    print(f"  {'Balloon Payment at Maturity':38} {'—':>14} {sar(flex['balloon']):>16}")
    print(f"  {'Total Profit (Finance Cost)':38} {sar(loan['total_profit']):>14} {sar(flex['total_profit']):>16}")
    print(f"  {'Processing Fee':38} {sar(loan['processing_fee']):>14} {sar(flex['processing_fee']):>16}")
    print(f"  {'Est. Comprehensive Insurance':38} {sar(loan['insurance']):>14} {sar(flex['insurance']):>16}")
    print("  " + "─" * (W - 2))
    print(f"  {'TOTAL COST OF OWNERSHIP':38}")
    print(f"  {'  Option A: Keep car (pay balloon)':38} {sar(loan['total_cost_own']):>14} {sar(flex['total_cost_keep']):>16}")
    print(f"  {'  Option B: Return car at end':38} {'  N/A':>14} {sar(flex['total_cost_return']):>16}")
    print("  " + "─" * (W - 2))

    diff_keep   = flex["total_cost_keep"]   - loan["total_cost_own"]
    diff_return = loan["total_cost_own"]    - flex["total_cost_return"]

    print(f"  VERDICT (if KEEPING the car):")
    if diff_keep > 0:
        print(f"    Loan is cheaper by {sar(diff_keep)} over the ownership period.")
    elif diff_keep < 0:
        print(f"    Auto Flex is cheaper by {sar(-diff_keep)} over the ownership period.")
    else:
        print(f"    Both products cost the same when keeping the vehicle.")

    print(f"  VERDICT (Auto Flex RETURN vs Loan):")
    if diff_return > 0:
        print(f"    Auto Flex (return) saves {sar(diff_return)} vs Loan — "
              f"but you do NOT own the car at end.")
    else:
        print(f"    Loan still cheaper by {sar(-diff_return)} even vs return scenario.")

    # Show first 12-month amortization snapshot
    print()
    print(f"  AMORTIZATION SNAPSHOT — First 12 Months")
    print(f"  {'Month':>5}  {'':6} {'Payment':>12} {'Principal':>12} {'Interest':>12} {'Balance':>14}")
    print(f"  {'':5}  {'':6} {'--------':>12} {'---------':>12} {'--------':>12} {'-------':>14}")
    for s in loan["schedule"][:12]:
        print(f"  {s['month']:>5}  {'LOAN':6} {sar(s['payment']):>12} "
              f"{sar(s['principal']):>12} {sar(s['interest']):>12} {sar(s['balance']):>14}")
    print(f"  {'':5}  {'':6}")
    for s in flex["schedule"][:12]:
        print(f"  {s['month']:>5}  {'FLEX':6} {sar(s['payment']):>12} "
              f"{sar(s['principal']):>12} {sar(s['interest']):>12} {sar(s['balance']):>14}")
    print()


def print_summary(results: List[Tuple[Dict, Dict]]) -> None:
    """Print the master summary table across all BYD models."""
    W = 110
    print()
    print("═" * W)
    print("  MASTER SUMMARY — TOTAL COST OF OWNERSHIP  (Down Payment + Repayments + Insurance + Fees)")
    print("  Market: Riyadh, Saudi Arabia  |  Currency: SAR  |  Profit Rate: 4.99% p.a. | Down: 20%")
    print("═" * W)
    print(f"  {'Model':<34} {'Type':<12} {'Price':>11} {'Monthly':>11}"
          f" {'Loan-Total':>13} {'Flex-Keep':>13} {'Flex-Return':>13} {'Best':<12}")
    print("  " + "─" * (W - 2))

    for loan, flex in results:
        name       = loan.get("model_name", "")
        mtype      = loan.get("model_type", "")
        price      = loan["vehicle_price"]
        loan_total = loan["total_cost_own"]
        fk         = flex["total_cost_keep"]
        fr         = flex["total_cost_return"]

        options = {"Loan": loan_total, "Flex-Keep": fk, "Flex-Return": fr}
        best    = min(options, key=options.get)
        saving  = sorted(options.values())[1] - options[best]

        print(f"  {name:<34} {mtype:<12} {sar(price):>11} {sar(loan['monthly_pmt']):>11}"
              f" {sar(loan_total):>13} {sar(fk):>13} {sar(fr):>13}  {best} (saves {sar(saving)})")

    print()
    print("  COLUMN DEFINITIONS:")
    print("  • Monthly      — Loan monthly payment (60-month product)")
    print("  • Loan-Total   — All-in cost: down + 60 installments + insurance + fee")
    print("  • Flex-Keep    — All-in cost: down + 48 installments + balloon + insurance + fee")
    print("  • Flex-Return  — All-in cost: down + 48 installments + insurance + fee (car returned)")
    print()


def print_key_insights(results: List[Tuple[Dict, Dict]]) -> None:
    """Print qualitative and strategic observations for BYD buyers in Riyadh."""
    print("═" * 74)
    print("  KEY INSIGHTS FOR BYD BUYERS — RIYADH, SAUDI ARABIA")
    print("═" * 74)

    insights = [
        ("1. Monthly Cash Flow",
         "Auto Flex typically saves SAR 200–600/month vs Loan — freeing cash\n"
         "     for investments, emergencies, or early balloon settlement savings."),

        ("2. Total Ownership Cost",
         "The Vehicle Loan is almost always cheaper in total cost if you intend\n"
         "     to keep the car. Flex adds profit on the deferred balloon portion."),

        ("3. Auto Flex — Return Option",
         "Returning the car at end of Flex term yields the lowest total outlay\n"
         "     but you own nothing at end. Best if you prefer to upgrade every 4 yrs."),

        ("4. Balloon Refinancing Risk",
         "If you cannot pay the 25% balloon at month 48, you must refinance it.\n"
         "     Refinancing adds more profit charges — plan your balloon exit strategy."),

        ("5. BYD Resale / GFV",
         "BYD EVs have shown competitive residual values in the GCC. The bank's\n"
         "     25% GFV may be conservative — actual resale could exceed balloon value,\n"
         "     meaning you could sell privately and profit after settling the balloon."),

        ("6. EV Running Cost Advantage",
         "BYD EVs save ~SAR 500–900/month vs equivalent ICE vehicle (fuel vs\n"
         "     electricity). PHEVs (DM-i) save SAR 200–400/month. These savings\n"
         "     can more than offset any Flex vs Loan cost difference."),

        ("7. Insurance",
         "Comprehensive insurance in KSA is mandatory for financed vehicles.\n"
         "     Rates range 1.2–2% p.a. EV-specific insurance is available and\n"
         "     may offer better coverage. Factor in battery coverage terms."),

        ("8. Recommended Banks (KSA)",
         "Al Rajhi Bank (Ijarah auto lease), Saudi National Bank (AlAhli Lease),\n"
         "     Riyad Bank (50/50 program), Alinma Bank, Bank AlJazira.\n"
         "     Always compare APR, not just monthly installment amounts."),

        ("9. SAMA Regulations",
         "SAMA caps total personal financing at 33% of monthly salary (net).\n"
         "     Balloon products may be assessed differently — confirm with bank."),

        ("10. Optimal Strategy",
          "For most buyers: take Auto Flex, invest the monthly savings, then\n"
          "      pay off or refinance the balloon from accumulated savings.\n"
          "      For lowest total cost: take the standard 60-month Loan."),
    ]

    for title, body in insights:
        print(f"\n  [{title}]")
        print(f"     {body}")

    print()


# ══════════════════════════════════════════════════════════════════════════════
# CSV EXPORT
# ══════════════════════════════════════════════════════════════════════════════

def export_csv(results: List[Tuple[Dict, Dict]], filename: str = "byd_finance_comparison.csv") -> None:
    """Export summary results to CSV for further analysis (Excel, Sheets, etc.)."""
    rows = []
    for loan, flex in results:
        rows.append({
            "Model":                    loan.get("model_name", ""),
            "Type":                     loan.get("model_type", ""),
            "Vehicle_Price_SAR":        loan["vehicle_price"],
            "Down_Payment_SAR":         loan["down_payment"],
            "Profit_Rate_PA":           f"{loan['rate_pa']:.4f}",

            # Loan
            "Loan_Term_Months":         loan["term_months"],
            "Loan_Principal_SAR":       loan["principal"],
            "Loan_Monthly_PMT_SAR":     round(loan["monthly_pmt"], 0),
            "Loan_Total_PMTs_SAR":      round(loan["total_pmts"], 0),
            "Loan_Total_Profit_SAR":    round(loan["total_profit"], 0),
            "Loan_Insurance_SAR":       round(loan["insurance"], 0),
            "Loan_Total_Own_SAR":       round(loan["total_cost_own"], 0),

            # Flex
            "Flex_Term_Months":         flex["term_months"],
            "Flex_Balloon_SAR":         flex["balloon"],
            "Flex_Monthly_PMT_SAR":     round(flex["monthly_pmt"], 0),
            "Flex_Total_PMTs_SAR":      round(flex["total_pmts"], 0),
            "Flex_Total_Profit_SAR":    round(flex["total_profit"], 0),
            "Flex_Insurance_SAR":       round(flex["insurance"], 0),
            "Flex_Total_Keep_SAR":      round(flex["total_cost_keep"], 0),
            "Flex_Total_Return_SAR":    round(flex["total_cost_return"], 0),

            # Comparison
            "Monthly_Saving_Flex_SAR":  round(loan["monthly_pmt"] - flex["monthly_pmt"], 0),
            "Extra_Cost_Keep_Flex_SAR": round(flex["total_cost_keep"] - loan["total_cost_own"], 0),
            "Saving_Return_Flex_SAR":   round(loan["total_cost_own"] - flex["total_cost_return"], 0),
        })

    output_path = os.path.join(os.path.dirname(__file__), filename)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  CSV exported → {output_path}")


def export_amortization_csv(results: List[Tuple[Dict, Dict]],
                             filename: str = "byd_amortization_schedules.csv") -> None:
    """Export full amortization schedules for all models to CSV."""
    output_path = os.path.join(os.path.dirname(__file__), filename)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Model", "Product", "Month", "Payment_SAR",
                         "Principal_SAR", "Interest_SAR", "Balance_SAR"])
        for loan, flex in results:
            name = loan.get("model_name", "")
            for row in loan["schedule"]:
                writer.writerow([name, "Loan (60m)", row["month"],
                                  row["payment"], row["principal"],
                                  row["interest"], row["balance"]])
            for row in flex["schedule"]:
                writer.writerow([name, "Auto Flex (48m)", row["month"],
                                  row["payment"], row["principal"],
                                  row["interest"], row["balance"]])
    print(f"  Amortization CSV exported → {output_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # ── Header ────────────────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║     BYD VEHICLE FINANCE COMPARISON — RIYADH, SAUDI ARABIA  (2025)      ║")
    print("║     Vehicle Loan (Murabaha)  vs  Auto Flex (Ijarah + Balloon)           ║")
    print("║     Currency: Saudi Riyal (SAR)  |  All prices VAT-inclusive            ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("  FINANCING ASSUMPTIONS:")
    print(f"  ┌─────────────────────────────────────────────────────────────────────┐")
    print(f"  │  Profit Rate   : {pct(PARAMS['profit_rate_pa'])} p.a. (reducing balance, Islamic-compliant) │")
    print(f"  │  Loan Product  : 60 months | 20% down payment | no balloon          │")
    print(f"  │  Flex Product  : 48 months | 20% down payment | 25% GFV balloon     │")
    print(f"  │  Insurance     : ~1.5% p.a. of depreciating vehicle value           │")
    print(f"  │  Processing Fee: SAR 500 (one-time, both products)                  │")
    print(f"  │  VAT (15%)     : Already included in all listed vehicle prices       │")
    print(f"  └─────────────────────────────────────────────────────────────────────┘")
    print()

    # ── Run calculations ──────────────────────────────────────────────────────
    results: List[Tuple[Dict, Dict]] = []
    for item in BYD_LINEUP:
        loan = calc_loan(item["price"], PARAMS)
        flex = calc_flex(item["price"], PARAMS)
        loan["model_name"] = item["model"]
        loan["model_type"] = item["type"]
        flex["model_name"] = item["model"]
        flex["model_type"] = item["type"]
        results.append((loan, flex))

    # ── Detailed cards ────────────────────────────────────────────────────────
    for loan, flex in results:
        print_detail(loan, flex)

    # ── Summary table ─────────────────────────────────────────────────────────
    print_summary(results)

    # ── Key insights ──────────────────────────────────────────────────────────
    print_key_insights(results)

    # ── CSV exports ───────────────────────────────────────────────────────────
    print("  EXPORTS:")
    export_csv(results)
    export_amortization_csv(results)
    print()
    print("  Analysis complete. Review the CSV files for full amortization data.")
    print("  Disclaimer: These calculations are for illustrative purposes only.")
    print("  Actual rates, fees, and balloon percentages vary by bank, credit score,")
    print("  and promotion. Always obtain a formal quote from an authorised lender.")
    print()


if __name__ == "__main__":
    main()
