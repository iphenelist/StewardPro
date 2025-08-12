# Departmental Budget Report

The Departmental Budget Report provides a comprehensive view of budget allocations versus actual expenses for church departments.

## Data Sources

### Primary Data Source: Department Budget DocType
The report now pulls budget allocation amounts from the **Department Budget** doctype instead of the Department doctype's annual_budget field. This allows for:
- Multiple budget periods per department
- Fiscal year-specific budgets
- Church-specific budget allocations
- Proper budget versioning and approval workflows

### Expense Data Source: Church Expense DocType
Actual expenses are pulled from the **Church Expense** doctype, filtered by:
- Department assignment
- Fiscal year dates
- Budget reference (if available)
- Document status (submitted only)

## Report Filters

### 1. Fiscal Year
- **Type**: Link to Fiscal Year doctype
- **Purpose**: Filter budgets and expenses by specific fiscal year
- **Behavior**: 
  - Filters Department Budget records by fiscal_year field
  - Filters Church Expense records by expense_date within fiscal year dates

### 2. Department
- **Type**: Link to Department doctype
- **Purpose**: Show budget data for specific department only
- **Behavior**: Filters both budget and expense data by department

### 3. Church
- **Type**: Link to Church doctype
- **Purpose**: Filter by specific church (for multi-church setups)
- **Behavior**: Filters Department Budget records by church field

## Report Columns

### 1. Department
- **Source**: Department.department_name
- **Type**: Data
- **Purpose**: Display department name

### 2. Code
- **Source**: Department.department_code
- **Type**: Data
- **Purpose**: Display department short code

### 3. Fiscal Year
- **Source**: Department Budget.fiscal_year
- **Type**: Link to Fiscal Year
- **Purpose**: Show which fiscal year the budget applies to

### 4. Allocated Amount
- **Source**: Department Budget.total_budget_amount
- **Type**: Currency
- **Purpose**: Show approved budget allocation

### 5. Actual Expenses
- **Source**: Sum of Church Expense.amount
- **Type**: Currency
- **Purpose**: Show total expenses incurred

### 6. Balance
- **Calculation**: Allocated Amount - Actual Expenses
- **Type**: Currency
- **Purpose**: Show remaining budget (positive) or overspend (negative)

### 7. Utilization %
- **Calculation**: (Actual Expenses / Allocated Amount) × 100
- **Type**: Percent
- **Purpose**: Show percentage of budget used

### 8. Status
- **Calculation**: Based on utilization percentage
- **Type**: Data
- **Values**:
  - "Over Budget" (>100%)
  - "Near Limit" (90-100%)
  - "On Track" (50-90%)
  - "Under Utilized" (<50%)

## Key Features

### 1. Fiscal Year Integration
- Properly handles fiscal year dates from Fiscal Year doctype
- Filters expenses by fiscal year start and end dates
- Supports multiple fiscal years per department

### 2. Budget Reference Tracking
- Links expenses to specific budget allocations
- Uses budget_reference field in Church Expense
- Ensures expenses are tracked against correct budget period

### 3. Multi-Church Support
- Filters by church when specified
- Supports organizations with multiple church locations
- Maintains separate budgets per church

### 4. Status Indicators
- Visual status indicators for budget health
- Color-coded utilization levels
- Quick identification of budget issues

## Usage Scenarios

### 1. Monthly Budget Review
- Filter by current fiscal year
- Review all departments
- Identify over-budget departments
- Plan corrective actions

### 2. Department-Specific Analysis
- Filter by specific department
- Compare across fiscal years
- Track department spending trends
- Evaluate budget adequacy

### 3. Church Comparison
- Filter by different churches
- Compare budget utilization
- Identify best practices
- Standardize budget processes

### 4. Year-End Analysis
- Review full fiscal year performance
- Identify budget variances
- Plan next year's budgets
- Generate board reports

## Data Relationships

```
Department Budget (Primary)
├── Links to Department (for department details)
├── Links to Fiscal Year (for date ranges)
├── Links to Church (for multi-church filtering)
└── Referenced by Church Expense (budget_reference field)

Church Expense (Secondary)
├── Links to Department (for department filtering)
├── Has expense_date (for fiscal year filtering)
├── Has budget_reference (for budget linking)
└── Aggregated for actual expenses
```

## Report Logic

1. **Query Department Budgets**: Get all approved budget allocations matching filters
2. **Join Department Data**: Get department names and codes
3. **Calculate Expenses**: For each budget, sum related expenses
4. **Apply Filters**: Filter expenses by fiscal year dates and other criteria
5. **Calculate Metrics**: Compute balance, utilization, and status
6. **Format Output**: Present data in structured columns

## Integration Points

- **Department DocType**: Department details and hierarchy
- **Department Budget DocType**: Budget allocations and approvals
- **Church Expense DocType**: Actual spending data
- **Fiscal Year DocType**: Date ranges and periods
- **Church DocType**: Multi-location support

This report provides comprehensive budget oversight and is essential for financial management and accountability in church operations.
