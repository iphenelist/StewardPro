# Department Income DocType

The Department Income DocType is designed to track income specifically at the Department level in the StewardPro Church Management System.

## Features

### Core Fields
- **Date**: Transaction date for the income record
- **Department**: Link to the Department receiving the income
- **Department Code**: Auto-fetched department code (read-only)
- **Income Type**: Category of income (Tithe, Offering, Donation, Fund Raising, Grant, Other)
- **Amount**: Income amount (must be positive)
- **Payment Mode**: Method of payment (Cash, Cheque, Bank Transfer, Mpesa, Credit Card, Other)
- **Receipt Number**: Unique receipt identifier
- **Description**: Detailed description of the income
- **Notes**: Additional notes

## Key Functionality

### 1. Department-Level Income Tracking
- Records income for specific departments
- Supports multiple income types per department
- Tracks payment methods for audit purposes

### 2. Validation Features
- Ensures department exists and is active
- Validates amount is positive
- Auto-fetches department code from department
- Supports document amendments

### 3. Integration with Department DocType
The Department DocType includes new methods for income calculations:
- `get_department_income()`: Get income records for a department
- `get_total_income(year)`: Calculate total income for a year
- `get_income_by_type(year)`: Get income breakdown by type
- `get_department_balance(year)`: Calculate balance (income - expenses)

## Reports

### 1. Department Income Report
- View all department income transactions
- Filter by date range, department, income type, and payment mode
- Displays income summary by department and type
- Supports export and printing

### 2. Department Balance Report
- Shows income, expenses, and balance for each department
- Calculates net balance (income - expenses)
- Supports date range filtering
- Useful for financial analysis

### 3. Financial Summary Report (Updated)
- Now includes department-level income data
- Shows department income trends
- Compares current month vs previous month and year-to-date

## Permissions

- **System Manager**: Full access (create, read, write, delete, export, print)
- **Treasurer**: Full access (create, read, write, delete, export, print)
- **Department Head**: Can create and read (no delete), can export and print
- **Elder**: Read-only access (export and print only)

## Usage Workflow

1. **Record Income**: Create a new Department Income record with date, department, type, and amount
2. **Submit**: Submit the record to make it official
3. **View Reports**: Use Department Income Report to view all transactions
4. **Analyze Balance**: Use Department Balance Report to see income vs expenses
5. **Financial Summary**: Check Financial Summary for overall financial health

## Integration Points

- **Department DocType**: Parent relationship for income tracking
- **Department Expense DocType**: Used for balance calculations
- **Financial Summary Report**: Includes department income data
- **Workspace**: Added to StewardPro workspace for easy access

## Sample Data

The system supports recording income for any active department with various income types:
- Tithes from members
- Offerings during services
- Donations for specific causes
- Fund raising activities
- Grants from organizations
- Other miscellaneous income

## Testing

Unit tests are included in `test_department_income.py` covering:
- Creating department income records
- Validating amount is positive
- Validating department exists
- Testing amendments

