# Banking Features Documentation

## Overview

The AI Widget Chat application now includes comprehensive banking features that allow users to interact with banking data through natural language queries. The system includes 5 main banking widgets:

1. **Banking Accounts Widget** - View and manage bank accounts
2. **Banking Transactions Widget** - View account transactions
3. **Banking Offers Widget** - View available banking offers and promotions
4. **Banking Payments Widget** - Access payment methods and links
5. **Banking Banker Widget** - Contact banker information and availability

## Architecture

### Backend Components

#### 1. Banking API Service (`backend/app/services/banking_api.py`)

- **Purpose**: Handles all banking-related API calls and data management
- **Features**:
  - Mock data generation for development and testing
  - Support for real banking API integration
  - Comprehensive error handling and fallback mechanisms
  - Rate limiting and timeout management

#### 2. Banking Widgets (`backend/app/widgets/banking/`)

- **BaseBankingWidget**: Common functionality for all banking widgets
- **AccountsWidget**: Displays account information with balance and status
- **TransactionsWidget**: Shows transaction history with filtering options
- **OffersWidget**: Displays banking offers with expiration tracking
- **PaymentsWidget**: Shows payment methods with fees and processing times
- **BankerWidget**: Lists banker contacts with availability status

#### 3. LLM Service Integration (`backend/app/services/llm_service.py`)

- **Function Declarations**: 5 new banking functions for the AI model
- **Keyword Detection**: Enhanced to recognize banking-related queries
- **Widget Extraction**: Automatic widget creation based on user intent

### Frontend Components

#### 1. Widget Component Updates (`frontend/src/app/components/widgets/widget/`)

- **New Icons**: Banking-specific icons for each widget type
- **Data Extraction**: Methods to extract banking data from widgets
- **Template Updates**: HTML templates for all banking widgets

#### 2. Widget Service Updates (`frontend/src/app/services/widget.service.ts`)

- **Data Extraction**: Methods to extract banking widget data
- **Type Safety**: TypeScript interfaces for banking data structures

## Features

### 1. Banking Accounts Widget

**Purpose**: Display all bank accounts with balances and account information

**Features**:

- Account type filtering (checking, savings, credit, investment, business)
- Balance display with positive/negative indicators
- Account status and last activity information
- Total balance summary
- Account grouping by type

**User Queries**:

- "Show my accounts"
- "List my checking accounts"
- "What's my account balance?"
- "Show my savings accounts"

### 2. Banking Transactions Widget

**Purpose**: Display transaction history for specific accounts

**Features**:

- Transaction filtering by type (debit, credit, transfer, payment, deposit, withdrawal)
- Transaction amount display with debit/credit indicators
- Merchant and description information
- Transaction status and date formatting
- Account balance display
- Transaction grouping by date

**User Queries**:

- "Show transactions for account ACC001"
- "Show my recent transactions"
- "List debit transactions"
- "Show payment history"

### 3. Banking Offers Widget

**Purpose**: Display available banking offers and promotions

**Features**:

- Offer categorization (savings, credit, investment, loans, mortgage)
- Expiration tracking with days remaining
- Offer value and requirements display
- Priority-based sorting
- Active/expired offer filtering

**User Queries**:

- "Show banking offers"
- "What savings offers are available?"
- "Show credit card promotions"
- "List investment offers"

### 4. Banking Payments Widget

**Purpose**: Display payment methods and options

**Features**:

- Payment type filtering (self, 3rd_party, bill_pay, international)
- Fee and processing time display
- Recommended payment method highlighting
- Payment method comparison
- Free vs. paid method identification

**User Queries**:

- "Show payment options"
- "How can I send money to someone?"
- "What are the fees for wire transfers?"
- "Show international payment methods"

### 5. Banking Banker Widget

**Purpose**: Display banker contact information and availability

**Features**:

- Department filtering (personal_banking, business_banking, investment_services, etc.)
- Specialization filtering (wealth_management, small_business, retirement_planning, etc.)
- Availability status and contact methods
- Experience and language information
- Direct contact and scheduling options

**User Queries**:

- "Show banker contacts"
- "Find a wealth management advisor"
- "Who can help with business banking?"
- "Show available bankers"

## API Endpoints

### Banking Function Declarations

The LLM service includes 5 new function declarations:

1. **get_banking_accounts**

   - Parameters: `account_type` (optional)
   - Returns: Account list with balances and details

2. **get_account_transactions**

   - Parameters: `account_id` (required), `limit`, `transaction_type`
   - Returns: Transaction history for specific account

3. **get_banking_offers**

   - Parameters: `category`, `limit`
   - Returns: Available banking offers

4. **get_payment_links**

   - Parameters: `payment_type` (required), `amount`, `recipient`
   - Returns: Payment methods and links

5. **get_banker_contacts**
   - Parameters: `department`, `specialization`
   - Returns: Banker contact information

## Data Structures

### Account Data

```json
{
  "id": "ACC001",
  "account_number": "****1234",
  "type": "checking",
  "name": "Primary Checking",
  "balance": 2547.89,
  "currency": "USD",
  "status": "active",
  "last_activity": "2024-01-15T10:30:00Z"
}
```

### Transaction Data

```json
{
  "id": "TXN1001",
  "account_id": "ACC001",
  "type": "debit",
  "amount": -25.5,
  "description": "Starbucks - Debit",
  "merchant": "Starbucks",
  "date": "2024-01-15T10:30:00Z",
  "status": "completed",
  "category": "food"
}
```

### Offer Data

```json
{
  "id": "OFFER001",
  "title": "High Yield Savings Bonus",
  "description": "Earn 5.25% APY on new savings deposits up to $10,000",
  "category": "savings",
  "type": "bonus",
  "value": "$525",
  "valid_until": "2024-03-31T23:59:59Z",
  "requirements": "Minimum $1,000 deposit",
  "status": "active"
}
```

## Usage Examples

### Natural Language Queries

Users can interact with banking features using natural language:

```
User: "Show my accounts"
AI: [Creates banking accounts widget with all accounts]

User: "What's my checking account balance?"
AI: [Creates banking accounts widget filtered to checking accounts]

User: "Show transactions for my savings account"
AI: [Creates banking transactions widget for savings account]

User: "What banking offers are available?"
AI: [Creates banking offers widget with all offers]

User: "How can I send money to someone?"
AI: [Creates banking payments widget with 3rd party payment options]

User: "I need help with investment planning"
AI: [Creates banking banker widget filtered to investment services]
```

### Widget Actions

Each banking widget includes relevant actions:

- **Refresh**: Update widget data
- **Filter**: Filter data by various criteria
- **Export**: Export data to PDF/CSV
- **Contact**: Contact relevant banking personnel
- **Schedule**: Schedule appointments with bankers

## Configuration

### Widget Configuration

Each banking widget supports configuration options:

```json
{
  "size": "medium",
  "theme": "banking",
  "show_balances": true,
  "show_last_activity": true,
  "refresh_interval": 300,
  "security_level": "high"
}
```

### Refresh Intervals

- **Banking Accounts**: 5 minutes
- **Banking Transactions**: 1 minute
- **Banking Offers**: 1 hour
- **Banking Payments**: 5 minutes
- **Banking Banker**: 30 minutes

## Security Considerations

### Data Protection

- All banking data is handled securely
- Mock data is used for development and testing
- Real banking APIs should implement proper authentication
- Sensitive information is masked in display

### Widget Security

- Banking widgets have high security level
- Auto-refresh is enabled for real-time data
- Error handling prevents data leakage
- User authentication required for real banking data

## Testing

### Test Coverage

- Unit tests for all banking API methods
- Widget creation and data formatting tests
- LLM integration tests
- Frontend component tests

### Test Script

Run the integration test:

```bash
python3 test_banking_integration.py
```

## Future Enhancements

### Planned Features

1. **Real Banking API Integration**: Connect to actual banking APIs
2. **Advanced Filtering**: More sophisticated filtering options
3. **Data Visualization**: Charts and graphs for banking data
4. **Notifications**: Real-time banking notifications
5. **Mobile Optimization**: Enhanced mobile banking experience

### API Integrations

- Open Banking APIs
- Plaid integration
- Yodlee integration
- Custom banking APIs

## Conclusion

The banking features provide a comprehensive solution for banking data interaction through natural language queries. The system is designed to be extensible, secure, and user-friendly, with proper separation of concerns between API services, widgets, and frontend components.

All banking features are fully integrated and tested, ready for production use with proper banking API credentials.
