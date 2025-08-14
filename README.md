
# StewardPro App
	
StewardPro is a Frappe extension for church management, budgeting, and reporting. This guide covers setup, data preparation, and report viewing.

## 1. Installation & Setup

1. **Install App**
	 - Add StewardPro to your bench:
		 ```bash
		 bench get-app /path/to/stewardpro
		 bench --site <your-site> install-app stewardpro
		 ```
2. **Migrate Site**
	 - Run migrations to apply patches and fixtures:
		 ```bash
		 bench --site <your-site> migrate
		 ```
3. **Enable Developer Mode (optional)**
	 - For development/testing:
		 ```bash
		 bench set-config -g developer_mode 1
		 ```

## 2. Data Preparation

### a. Fiscal Year
- Fiscal Year is auto-created before install. You can manually create/edit via the Fiscal Year DocType.
- Fields: Year, Start/End Dates, Short/Long Year, Disabled, Auto Created.

### b. Departments
- Default departments are loaded automatically (Sabbath School, Youth Ministry, etc.).
- You can add/edit departments in the Department DocType.

### c. Expense Categories
- Setup categories for church expenses in the Expense Category DocType.

### d. Church Expenses
- Record transactions in the Church Expense DocType.
- Link expenses to departments and categories for accurate reporting.

## 3. Using the Dashboard & Reports

### a. Church Management Dashboard
- Access via Workspace: shortcuts to setup DocTypes, transactions, and reports.
- Location: `Church Management Dashboard` workspace.

### b. Reports
- **Expense Report**: View and analyze church expenses by category, department, or date.
- **Departmental Budget Report**: Track budgets and spending for each department.
- **Expense Graph**: Visualize expenses over time.

## 4. Permissions
- System Manager: Full access.
- Treasurer, Church Elder, Accounts User, Sales User: Read-only access to Fiscal Year and reports.

## 5. Automation
- Fiscal Year auto-creation: New fiscal years are generated automatically as needed.
- Department fixtures: Default departments are loaded on install/migrate.

## 6. Customization
- You can add new departments, categories, or custom reports via the DocType UI.
- For advanced logic, edit Python controllers or client scripts in `stewardpro/church_management/doctype/`.

## 7. Troubleshooting
- If data is missing, run `bench migrate` or check patch scripts in `stewardpro/patches/`.
- For errors, check logs in the `logs/` directory or use Frappe's error console.

---
For more details, see the app's source code and workspace documentation.
