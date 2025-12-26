# Testing Guide

This guide shows you how to test the Multi-Currency Savings Advisor.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## Testing Methods

### Method 1: Run Unit Tests (Automated)

Test the core functionality with automated unit tests:

```bash
python -m unittest discover -s tests -v
```

**Expected Result:** All 25 tests should pass
- Currency model tests (11 tests)
- Savings goal tests (14 tests)

### Method 2: Run Demo Script (Feature Showcase)

See all features in action with the demo script:

```bash
python demo.py
```

**What it demonstrates:**
1. Exchange rate fetching and display
2. Depositing money in multiple currencies
3. Viewing portfolio balances
4. Currency conversion
5. Creating savings goals
6. Contributing to goals
7. Goal progress tracking
8. Intelligent recommendations
9. Portfolio analysis
10. Optimal allocation calculator
11. Transaction history

### Method 3: Interactive CLI (Manual Testing)

Run the full application interactively:

```bash
python main.py
```

**Try these workflows:**

#### Workflow 1: Basic Portfolio Management
1. Start the app
2. Choose option 4 (Deposit Money)
   - Deposit $1000 USD
3. Choose option 2 (View Currency Balances)
   - See your balance
4. Choose option 3 (View Exchange Rates)
   - Check current rates

#### Workflow 2: Currency Transfer
1. Choose option 4 (Deposit Money)
   - Deposit £500 GBP
2. Choose option 6 (Transfer Between Currencies)
   - Convert £200 GBP to USD
3. Choose option 2 (View Currency Balances)
   - See updated balances

#### Workflow 3: Savings Goals
1. Choose option 8 (Create Savings Goal)
   - Name: "Emergency Fund"
   - Currency: USD
   - Target: $5000
   - Deadline: 180 days from now
2. Choose option 9 (Contribute to Goal)
   - Contribute $500 to Emergency Fund
3. Choose option 7 (View Savings Goals)
   - See progress (10% complete)
4. Choose option 10 (Get Savings Recommendations)
   - See how much to save daily

#### Workflow 4: Multi-Currency Strategy
1. Choose option 4 (Deposit Money)
   - Deposit in all currencies:
     - SAR 5000
     - USD 2000
     - GBP 1000
     - NGN 300000
2. Choose option 12 (Calculate Optimal Allocation)
   - Input USD 10000
   - See recommended distribution
3. Choose option 10 (Get Savings Recommendations)
   - Get diversification advice

## Test Scenarios

### Scenario 1: New User Setup
```bash
python main.py
```
1. View exchange rates (option 3)
2. Deposit money in your local currency (option 4)
3. Create your first savings goal (option 8)
4. Get recommendations (option 10)

### Scenario 2: Goal Tracking
```bash
python main.py
```
1. Create multiple goals in different currencies
2. Make regular contributions
3. Track progress over time
4. Get daily savings recommendations

### Scenario 3: Portfolio Rebalancing
```bash
python main.py
```
1. Check current balances (option 2)
2. Get recommendations (option 10)
3. Transfer between currencies (option 6)
4. View transaction history (option 11)

## Verification Checklist

After testing, verify:

- [ ] Exchange rates are displayed correctly
- [ ] Can deposit in all 4 currencies (SAR, USD, GBP, NGN)
- [ ] Can withdraw money (with insufficient funds check)
- [ ] Currency conversion works with correct exchange rates
- [ ] Can create savings goals with deadlines
- [ ] Progress percentage calculates correctly
- [ ] Daily savings needed is accurate
- [ ] Recommendations appear based on portfolio state
- [ ] Transaction history records all operations
- [ ] Optimal allocation adds up to 100%
- [ ] Total portfolio value is correct across currencies

## Common Issues

### Issue: "No module named requests"
**Solution:** Run `pip install -r requirements.txt`

### Issue: Exchange rates show "Fallback Rates"
**Explanation:** This is normal if internet is unavailable. The app uses reliable offline rates.

### Issue: "Insufficient funds" error
**Solution:** Ensure you have enough balance in the currency account before withdrawing or contributing to goals.

## Performance Tests

### Test 1: Large Transaction Volume
Create 100+ transactions and verify performance:
```python
for i in range(100):
    portfolio.deposit(Money(10, Currency.USD), f"Test deposit {i}")
```

### Test 2: Multiple Goals
Create 10+ savings goals and verify all tracking works correctly.

### Test 3: Currency Conversion Accuracy
Verify that converting A→B→A returns approximately the original amount (accounting for rounding).

## Next Steps

After testing:
1. Review the code structure in `src/`
2. Check the documentation in `README.md`
3. Read the technical overview in `PROJECT_OVERVIEW.md`
4. Try extending with new features
5. Run with real savings data

## Support

If you encounter issues:
1. Check that all dependencies are installed
2. Verify Python version is 3.7+
3. Review error messages carefully
4. Check the test output for specific failures

Happy Testing! 🎯
