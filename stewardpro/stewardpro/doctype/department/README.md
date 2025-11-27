# Department DocType

The Department DocType is designed to manage church departments and their budgets within the StewardPro Church Management System.

## Features

### Core Fields
- **Department Name**: Unique name for the department
- **Department Code**: Short code for easy identification (automatically converted to uppercase)
- **Description**: Detailed description of the department's purpose
- **Is Active**: Toggle to enable/disable departments
- **Parent Department**: Support for hierarchical department structure

### Contact Information
- **Department Head**: Link to Church Member who leads the department
- **Contact Email**: Department's contact email
- **Contact Phone**: Department's contact phone number

### Budget Management
- **Annual Budget**: Budget allocated for the department
- **Budget Year**: Year for which the budget is allocated (defaults to current year)

## Key Functionality

### 1. Department Hierarchy
- Supports parent-child relationships between departments
- Prevents circular references (department cannot be its own parent)
- Provides hierarchy path display (e.g., "Ministries > Youth Ministry")

### 2. Budget Tracking
- Tracks annual budget allocations
- Calculates total budget including child departments
- Provides budget utilization reports
- Integrates with expense tracking

### 3. Validation Features
- Automatic uppercase conversion for department codes
- Unique department names and codes
- Default budget year assignment
- Parent department validation

### 4. API Methods

#### `get_child_departments()`
Returns all active child departments

#### `get_department_hierarchy()`
Returns the full hierarchy path as a string

#### `get_total_budget_allocated()`
Calculates total budget including child departments

#### `get_department_expenses(from_date, to_date)`
Returns expenses for the department within date range

#### `get_budget_utilization(year)`
Returns budget utilization statistics including:
- Total budget
- Total expenses
- Remaining budget
- Utilization percentage

### 5. Global Functions

#### `get_department_tree()`
Returns department hierarchy as tree structure for tree view

#### `get_active_departments()`
Returns all active departments for dropdowns/selections

## Usage in Reports

The Department DocType is integrated with:
- **Departmental Budget Report**: Shows budget vs actual expenses
- **Expense Reports**: Filter expenses by department
- **Budget Utilization Reports**: Track department spending

## Sample Data

The system includes sample departments:
- Youth Ministry (YTH) - $15,000
- Music Ministry (MUS) - $8,000
- Children Ministry (CHI) - $12,000
- Evangelism (EVA) - $20,000
- Administration (ADM) - $25,000
- Maintenance (MNT) - $18,000
- Women's Ministry (WOM) - $6,000
- Men's Ministry (MEN) - $5,000

## JavaScript Features

### Form View
- Custom buttons for viewing expenses and budget reports
- Budget utilization popup with visual progress bar
- Automatic department code formatting
- Parent department validation

### List View
- Active/Inactive indicators
- Budget amount formatting
- Department tree view access
- Budget summary popup

### Tree View
- Hierarchical department display
- Add department functionality
- Filter by active status
- Expandable tree structure

## Integration

The Department DocType integrates seamlessly with:
- Church Expense tracking
- Budget management
- Reporting system
- Church Member management
- Workspace navigation

## Testing

Comprehensive test suite includes:
- Department creation and validation
- Hierarchy functionality
- Budget calculations
- Code formatting
- Parent-child relationships
