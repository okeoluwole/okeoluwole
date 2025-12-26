# Multi-Currency Finance Savings Advisor

A powerful financial planning tool that helps you manage and optimize savings across multiple currencies.

## Overview

This application provides intelligent savings advice and portfolio management for:
- Saudi Riyals (SAR)
- United States Dollars (USD)
- British Pounds (GBP)
- Nigerian Naira (NGN)

## Features

- **Multi-Currency Portfolio Management**: Track balances across multiple currencies
- **Real-Time Exchange Rates**: Live currency conversion with automatic fallback
- **Savings Goals**: Create and track savings goals with deadline monitoring
- **Smart Recommendations**: AI-powered advice on currency allocation and savings strategies
- **Transaction History**: Complete record of all deposits, withdrawals, and transfers
- **Interactive CLI**: User-friendly command-line interface with color-coded outputs

## Installation

1. Clone this repository:
```bash
git clone https://github.com/okeoluwole/okeoluwole.git
cd okeoluwole
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Main Features

#### 1. Portfolio Management
- View portfolio summary with total balance
- Check individual currency balances
- Deposit and withdraw money
- Transfer between currencies

#### 2. Savings Goals
- Create savings goals with target amounts
- Set deadlines for goal achievement
- Track progress with percentage completion
- Get daily savings recommendations

#### 3. Exchange Rates
- View current exchange rates for all currencies
- Automatic hourly updates
- Offline fallback rates for reliability

#### 4. Savings Recommendations
- Get personalized savings advice
- Currency diversification suggestions
- Goal achievement strategies
- Risk warnings for concentrated holdings

## Example Usage

```
Main Menu:
1.  View Portfolio Summary
2.  View Currency Balances
3.  View Exchange Rates
4.  Deposit Money
5.  Withdraw Money
6.  Transfer Between Currencies
7.  View Savings Goals
8.  Create Savings Goal
9.  Contribute to Goal
10. Get Savings Recommendations
11. View Transaction History
12. Calculate Optimal Allocation
0.  Exit
```

## Project Structure

```
├── src/
│   ├── models/              # Data models (Currency, Portfolio, Goals)
│   ├── services/            # Business logic (Exchange rates, Advisor)
│   └── cli.py              # Command-line interface
├── tests/                   # Unit tests
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── PROJECT_OVERVIEW.md     # Detailed technical documentation
└── README.md              # This file
```

## Technical Details

- **Language**: Python 3.7+
- **Architecture**: Clean architecture with separation of concerns
- **Exchange Rate API**: exchangerate-api.com
- **UI**: Colorama for terminal colors, Tabulate for formatted tables

## Features in Detail

### Currency Support
- Full support for SAR, USD, GBP, and NGN
- Currency symbols and country information
- Type-safe currency operations

### Intelligent Recommendations
The advisor provides three priority levels:
- **HIGH**: Urgent actions (overdue goals, at-risk savings)
- **MEDIUM**: Important suggestions (diversification, goal tracking)
- **LOW**: Optional optimizations (currency conversions)

### Goal Tracking
- Multiple goals per portfolio
- Deadline monitoring
- Daily savings calculator
- Progress tracking
- Status indicators

## Requirements

- Python 3.7 or higher
- Internet connection (for live exchange rates)
- Terminal with color support

## Dependencies

- requests: HTTP library for API calls
- python-dateutil: Date manipulation
- tabulate: Table formatting
- colorama: Terminal colors

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

MIT License - feel free to use this project for personal or commercial purposes.

## About

Created by @okeoluwole

- Interested in developing contech, proptech and project management web applications
- Currently learning automation
- Looking to collaborate on AI automation tools and application development
- Contact: okeoluwole@gmail.com
- Fun fact: I do marathons!
