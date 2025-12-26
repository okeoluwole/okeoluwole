# Multi-Currency Finance Savings Advisor

A comprehensive financial planning tool that helps you manage savings across multiple currencies with intelligent recommendations.

## Supported Currencies

- **SAR** - Saudi Riyal (﷼)
- **USD** - United States Dollar ($)
- **GBP** - British Pound (£)
- **NGN** - Nigerian Naira (₦)

## Features

### 1. Multi-Currency Portfolio Management
- Manage separate accounts for each supported currency
- Track balances across all currencies
- View total portfolio value in any currency
- Real-time currency conversion

### 2. Exchange Rate Service
- Fetches live exchange rates from external API
- Automatic fallback to offline rates if API unavailable
- Hourly rate refresh with caching
- Support for currency conversion between any pair

### 3. Savings Goals Tracking
- Create unlimited savings goals in any currency
- Set target amounts and deadlines
- Track progress with percentage completion
- Calculate daily savings needed to meet goals
- Monitor goal status (Not Started, In Progress, Completed, Overdue)

### 4. Intelligent Savings Advisor
- Portfolio analysis and insights
- Currency concentration risk warnings
- Goal achievement recommendations
- Currency diversification advice
- Optimal allocation calculations
- Priority-based recommendation system

### 5. Transaction Management
- Record deposits and withdrawals
- Transfer money between currency accounts
- View complete transaction history
- Track all financial movements

### 6. Interactive CLI Interface
- User-friendly menu system
- Colorful output with priority indicators
- Detailed portfolio summaries
- Real-time currency rate displays
- Transaction history viewing

## Architecture

```
multi-currency-savings-advisor/
├── src/
│   ├── models/
│   │   ├── currency.py         # Currency enums and Money class
│   │   ├── savings_goal.py     # Savings goal tracking
│   │   └── portfolio.py        # Multi-currency portfolio
│   ├── services/
│   │   ├── exchange_rate_service.py  # Currency conversion
│   │   └── savings_advisor.py        # Recommendation engine
│   └── cli.py                  # Command-line interface
├── tests/                      # Unit tests
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # User documentation
```

## Key Components

### Currency Model
- Enum-based currency definitions
- Money class with arithmetic operations
- Currency information (symbols, names, countries)
- Type-safe currency operations

### Portfolio Model
- Multi-currency account management
- Transaction recording
- Balance tracking per currency
- Savings goal integration

### Exchange Rate Service
- API integration for live rates
- Caching mechanism
- Fallback offline rates
- Cross-currency conversion

### Savings Advisor
- Portfolio analysis
- Multi-level recommendations (High/Medium/Low priority)
- Currency diversification strategies
- Goal achievement tracking
- Risk assessment

## Recommendation Types

### Goal-Based Recommendations
- Overdue goal alerts
- Daily savings calculations
- Goal achievement tracking
- Progress warnings

### Currency-Based Recommendations
- Concentration risk warnings
- Currency weakness alerts
- Diversification suggestions
- Stability recommendations

### Portfolio-Based Recommendations
- Multi-currency distribution advice
- Optimal allocation strategies
- Balance preservation tips

## Data Flow

1. **User Input** → CLI Interface
2. **Portfolio Management** → Currency Accounts
3. **Exchange Rates** → External API / Fallback
4. **Analysis** → Savings Advisor
5. **Recommendations** → User Display

## Security & Reliability

- Input validation on all operations
- Type safety with Python dataclasses
- Error handling for network failures
- Graceful fallback for offline operation
- Transaction integrity checks

## Extensibility

The system is designed for easy extension:

- Add new currencies by updating the Currency enum
- Implement custom recommendation strategies
- Integrate different exchange rate providers
- Add new goal types or constraints
- Extend transaction types

## Use Cases

1. **International Workers**: Manage income across multiple currencies
2. **Global Investors**: Track diversified currency holdings
3. **Expatriates**: Plan savings in home and host country currencies
4. **Travelers**: Optimize currency holdings for upcoming trips
5. **Financial Planners**: Analyze multi-currency portfolios

## Technical Highlights

- **Clean Architecture**: Separation of models, services, and UI
- **Type Safety**: Extensive use of dataclasses and enums
- **Error Handling**: Comprehensive validation and error messages
- **User Experience**: Colorful CLI with clear visual indicators
- **Testability**: Modular design for easy unit testing
- **Scalability**: Easy to add new features and currencies
