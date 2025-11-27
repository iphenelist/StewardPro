# StewardPro - Church Financial Management System

## Application Overview

StewardPro is a comprehensive financial management system designed specifically for churches and religious organizations. It provides a centralized platform to manage departments, budgets, expenses, and generate detailed financial reports. StewardPro helps church leadership maintain financial transparency, track spending against budgets, and make informed financial decisions.

### Problem Solved
- **Centralized Financial Tracking**: Eliminates scattered spreadsheets and manual record-keeping
- **Budget Control**: Ensures departments stay within allocated budgets
- **Financial Transparency**: Provides clear visibility into church finances for leadership
- **Audit Trail**: Maintains complete records of all financial transactions
- **Role-Based Access**: Ensures appropriate staff have access to relevant financial data

---

## Key Features

✅ **Department Management** - Create and organize church departments (e.g., Worship, Education, Outreach)

✅ **Item Management** - Maintain a catalog of items/services used across departments with unique identification per department

✅ **Budget Planning** - Create detailed budgets for each department with line-item tracking

✅ **Expense Tracking** - Record and categorize expenses against department budgets in real-time

✅ **Budget Monitoring** - Track spending vs. budget with remaining balance calculations

✅ **Financial Reporting** - Generate comprehensive reports showing expenses by department and budget status

✅ **Role-Based Access Control** - Three-tier permission system for different user types

✅ **Audit Trail** - Complete history of all transactions and changes

---

## User Roles & Permissions

### 1. **Department Head**
**Responsibilities**: Manage department operations and budgets

**Permissions**:
- Create and manage department information
- View department transactions and reports
- Record expenses for their department
- View budget status and spending
- Print and export department reports
- Share reports with other users

**Typical Users**: Department leaders, ministry coordinators

---

### 2. **Treasurer**
**Responsibilities**: Manage all financial transactions and reporting

**Permissions**:
- Create and manage all budgets
- Record and approve all expenses
- View all financial transactions across departments
- Generate financial reports
- Print and export financial data
- Email reports to leadership
- Access all financial DocTypes

**Typical Users**: Church treasurer, finance committee members

---

### 3. **Elder**
**Responsibilities**: Full system access and oversight

**Permissions**:
- Full access to all features and data
- Create, read, update, and delete any record
- Manage user roles and permissions
- Generate all reports
- Share data with other users
- Complete system administration

**Typical Users**: Senior church leadership, finance committee chair

---

## Core Modules

### **Department Management**
Organize your church into functional departments for better financial tracking.

**Features**:
- Create departments with unique codes (e.g., MAJ for Majengo, UCH for Uchapishaji)
- Assign department heads
- Track department-specific budgets and expenses
- View department performance

---

### **Item Management**
Maintain a catalog of items and services used across your church.

**Features**:
- Create items with unique names and descriptions
- Assign items to specific departments
- Track standard costs for budgeting
- Items are uniquely identified by: **item_name-department_code**
  - Example: "Pen-MAJ" (Pen item in Majengo department)
  - Example: "Pen-UCH" (Pen item in Uchapishaji department)
- Mark items as active or inactive

---

### **Budget Management**
Plan and allocate financial resources for each department.

**Features**:
- Create annual or periodic budgets
- Add line items with quantities and unit prices
- Calculate total budgeted amounts
- Track budgeted vs. actual spending
- View remaining budget balance
- Monitor budget utilization

---

### **Expense Tracking**
Record and monitor all departmental expenses.

**Features**:
- Link expenses to specific budgets
- Record individual expense items with quantities and amounts
- Automatically calculate total expenses
- Track spending against budget allocations
- Update budget remaining amounts in real-time
- Maintain complete expense history

---

### **Reporting**
Generate comprehensive financial reports for analysis and decision-making.

**Features**:
- View expenses by department
- Compare actual spending vs. budgeted amounts
- Generate expense summaries
- Export reports for presentations
- Print reports for records
- Email reports to stakeholders

---

## User Guide

### **Creating a Department**

1. Navigate to **Department** in the menu
2. Click **+ New** to create a new department
3. Enter the following information:
   - **Department Name**: Full name (e.g., "Worship Ministry")
   - **Department Code**: Short code (e.g., "WOR")
   - **Description**: Brief description of the department
4. Click **Save**

---

### **Creating an Item**

1. Navigate to **Item** in the menu
2. Click **+ New** to create a new item
3. Enter the following information:
   - **Item Name**: Name of the item (e.g., "Pen", "Projector")
   - **Department**: Select the department this item belongs to
   - **Description**: What the item is used for
   - **Unit of Measure**: How it's measured (e.g., "Piece", "Hour")
   - **Standard Cost**: Average cost of the item
4. Click **Save**

**Note**: Items are uniquely identified by item_name + department combination. You can have "Pen" in multiple departments, but only one "Pen" per department.

---

### **Creating a Budget**

1. Navigate to **Department Budget** in the menu
2. Click **+ New** to create a new budget
3. Enter the following information:
   - **Budget Name**: Descriptive name (e.g., "2025 Worship Budget")
   - **Department**: Select the department
   - **Budget Period**: Start and end dates
4. In the **Budget Items** section, click **Add Row** for each line item:
   - **Item**: Select from your item catalog
   - **Description**: Details about this budget line
   - **Quantity**: How many units
   - **Unit Price**: Cost per unit
   - **Budgeted Amount**: Auto-calculated (Quantity × Unit Price)
5. Click **Save**

---

### **Recording an Expense**

1. Navigate to **Department Expense** in the menu
2. Click **+ New** to record a new expense
3. Enter the following information:
   - **Expense Date**: When the expense occurred
   - **Department**: Which department incurred the expense
   - **Budget Reference**: Link to the budget this expense relates to
4. In the **Expense Details** section, click **Add Row** for each expense item:
   - **Item**: Select the item purchased
   - **Description**: Details about the purchase
   - **Quantity**: How many units purchased
   - **Unit Price**: Price paid per unit
   - **Amount**: Auto-calculated (Quantity × Unit Price)
5. Click **Save**

**Result**: The budget's "Spent Amount" and "Remaining Amount" are automatically updated.

---

### **Viewing Reports**

1. Navigate to **Expense Report** in the menu
2. Use filters to narrow down data:
   - **Department**: View expenses for specific department(s)
   - **Date Range**: Select start and end dates
3. View the report showing:
   - Individual expenses with details
   - Total expenses by department
   - Budget vs. actual comparison
4. Click **Print** to print the report
5. Click **Export** to download as a file

---

## Common Workflows

### **Workflow 1: Annual Budget Planning**
1. Create departments for each ministry area
2. Create items used by each department
3. Create annual budget for each department
4. Allocate budget items and amounts
5. Share budget with department heads for review

### **Workflow 2: Monthly Expense Recording**
1. Department heads submit expense receipts
2. Treasurer records expenses in the system
3. System automatically updates budget remaining amounts
4. Monitor spending vs. budget in real-time

### **Workflow 3: Financial Reporting**
1. Generate expense reports by department
2. Compare actual spending vs. budgeted amounts
3. Identify departments over budget
4. Present reports to leadership for decision-making
5. Archive reports for audit purposes

---

## Important Notes

### **Item Uniqueness**
- Items are uniquely identified by the combination of **item_name** and **department**
- You can have an item named "Pen" in the Worship department AND in the Education department
- However, you cannot have two items named "Pen" in the same department
- The system will prevent duplicate items in the same department

### **Budget Tracking**
- When you record an expense, the budget's "Spent Amount" is automatically updated
- The "Remaining Amount" is calculated as: Budgeted Amount - Spent Amount
- If spending exceeds the budget, the remaining amount will be negative (shown in red)

### **Department Codes**
- Department codes should be short and unique (e.g., "MAJ", "UCH", "WOR")
- Codes are used in item identification and reports
- Choose codes that are meaningful to your organization

### **Role-Based Access**
- Users can only see data relevant to their role
- Department Heads see only their department's data
- Treasurers see all financial data
- Elders have complete system access
- Contact your system administrator to change user roles

### **Data Integrity**
- All transactions are recorded with timestamps
- Complete audit trail of who made changes and when
- Deleted records are archived, not permanently removed
- Regular backups ensure data safety

---

## Getting Help

For questions or issues:
1. Contact your **Treasurer** or **System Administrator**
2. Refer to this guide for step-by-step instructions
3. Check the **Important Notes** section above for common questions

---

**Version**: 1.0  
**Last Updated**: 2025-11-27

