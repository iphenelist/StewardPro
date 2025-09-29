# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Avg, Count, Sum
from frappe.utils import flt, nowdate, getdate


# Define custom functions for date operations - commented out to avoid CustomFunction issues
# def Year(field):
# 	return CustomFunction("YEAR", [field])

# def Month(field):
# 	return CustomFunction("MONTH", [field])

def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)

	# Ensure data is not None for Excel export
	if data is None:
		data = []

	chart = get_chart_data(data, filters)
	return columns, data, None, chart


def get_columns():
	return [
		{
			"label": _("Department"),
			"fieldname": "department_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Code"),
			"fieldname": "department_code",
			"fieldtype": "Data",
			"width": 80
		},
		{
			"label": _("Fiscal Year"),
			"fieldname": "fiscal_year",
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"width": 100
		},
		{
			"label": _("Allocated Amount"),
			"fieldname": "allocated_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Actual Expenses"),
			"fieldname": "actual_expenses",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Utilization %"),
			"fieldname": "utilization_percentage",
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		}
	]


def get_data(filters):
	DepartmentBudget = DocType("Department Budget")
	Department = DocType("Department")
	Expense = DocType("Department Expense")

	# Get budget allocations from Department Budget doctype
	budget_query = (
		frappe.qb.from_(DepartmentBudget)
		.left_join(Department)
		.on(DepartmentBudget.department == Department.name)
		.select(
			DepartmentBudget.department,
			Department.department_name,
			Department.department_code,
			DepartmentBudget.total_budget_amount.as_("allocated_amount"),
			DepartmentBudget.fiscal_year,
			DepartmentBudget.name.as_("budget_name")
		)
		.where(DepartmentBudget.docstatus >= 0)
		.where(Department.is_active == 1)
		.orderby(Department.department_name)
	)

	# Apply filters
	if filters.get("fiscal_year"):
		budget_query = budget_query.where(DepartmentBudget.fiscal_year == filters.get("fiscal_year"))

	if filters.get("department"):
		budget_query = budget_query.where(DepartmentBudget.department == filters.get("department"))

	if filters.get("church"):
		budget_query = budget_query.where(DepartmentBudget.church == filters.get("church"))

	budget_data = budget_query.run(as_dict=True)
	
	# Calculate actual expenses for each department
	for row in budget_data:
		# Get actual expenses for this department and fiscal year
		expense_query = (
			frappe.qb.from_(Expense)
			.select(Sum(Expense.total_amount).as_("total_expenses"))
			.where(Expense.docstatus == 1)
			.where(Expense.department == row.get("department"))
		)
		
		# Filter by budget reference if available
		if row.get("budget_name"):
			expense_query = expense_query.where(Expense.budget_reference == row.get("budget_name"))
		
		# Filter by fiscal year if specified
		if filters.get("fiscal_year"):
			# Get fiscal year dates from Fiscal Year doctype
			fiscal_year_doc = frappe.get_doc("Fiscal Year", filters.get("fiscal_year"))
			expense_query = expense_query.where(
				(Expense.expense_date >= fiscal_year_doc.year_start_date) &
				(Expense.expense_date <= fiscal_year_doc.year_end_date)
			)
		
		expense_result = expense_query.run(as_dict=True)
		actual_expenses = flt(expense_result[0]["total_expenses"]) if expense_result and expense_result[0]["total_expenses"] else 0
		
		# Calculate derived fields
		allocated_amount = flt(row.get("allocated_amount", 0))
		balance = allocated_amount - actual_expenses
		utilization_percentage = (actual_expenses / allocated_amount * 100) if allocated_amount > 0 else 0
		
		# Determine status
		if utilization_percentage > 100:
			status = "Over Budget"
		elif utilization_percentage > 90:
			status = "Near Limit"
		elif utilization_percentage > 50:
			status = "On Track"
		else:
			status = "Under Utilized"
		
		# Update row with calculated values
		row.update({
			"actual_expenses": actual_expenses,
			"balance": balance,
			"utilization_percentage": utilization_percentage,
			"status": status
		})
	
	return budget_data


def get_department_summary(filters):
	"""Get summary statistics for all departments"""
	DepartmentBudget = DocType("Department Budget")

	summary_query = (
		frappe.qb.from_(DepartmentBudget)
		.select(
			Count(DepartmentBudget.name).as_("total_departments"),
			Sum(DepartmentBudget.total_budget_amount).as_("total_allocated"),
			Avg(DepartmentBudget.total_budget_amount).as_("avg_allocation")
		)
		.where(DepartmentBudget.docstatus >= 0)
	)

	# Apply filters
	if filters.get("fiscal_year"):
		summary_query = summary_query.where(DepartmentBudget.fiscal_year == filters.get("fiscal_year"))

	if filters.get("department"):
		summary_query = summary_query.where(DepartmentBudget.department == filters.get("department"))

	if filters.get("church"):
		summary_query = summary_query.where(DepartmentBudget.church == filters.get("church"))

	summary_result = summary_query.run(as_dict=True)
	return summary_result[0] if summary_result else {}


def get_over_budget_departments(filters):
	"""Get departments that are over budget"""
	data = get_data(filters)
	over_budget = [row for row in data if row.get("utilization_percentage", 0) > 100]
	return over_budget


@frappe.whitelist()
def get_summary_data(filters=None):
	"""Get summary data for the budget report"""
	if not filters:
		filters = {}

	# Convert string filters to dict if needed
	if isinstance(filters, str):
		import json
		filters = json.loads(filters)

	DepartmentBudget = DocType("Department Budget")
	Expense = DocType("Department Expense")

	# Get budget summary
	budget_query = (
		frappe.qb.from_(DepartmentBudget)
		.select(
			Count(DepartmentBudget.name).as_("total_budgets"),
			Sum(DepartmentBudget.total_budget_amount).as_("total_allocated")
		)
		.where(DepartmentBudget.docstatus >= 0)
	)

	# Apply filters
	if filters.get("fiscal_year"):
		budget_query = budget_query.where(DepartmentBudget.fiscal_year == filters.get("fiscal_year"))

	if filters.get("department"):
		budget_query = budget_query.where(DepartmentBudget.department == filters.get("department"))

	budget_result = budget_query.run(as_dict=True)
	budget_data = budget_result[0] if budget_result else {}

	# Get expense summary
	expense_query = (
		frappe.qb.from_(Expense)
		.select(Sum(Expense.total_amount).as_("total_spent"))
		.where(Expense.docstatus == 1)
	)

	# Apply department filter for expenses
	if filters.get("department"):
		expense_query = expense_query.where(Expense.department == filters.get("department"))

	# Apply fiscal year filter for expenses (approximate by date range)
	if filters.get("fiscal_year"):
		# Get fiscal year dates
		fiscal_year_doc = frappe.get_doc("Fiscal Year", filters.get("fiscal_year"))
		expense_query = expense_query.where(
			(Expense.expense_date >= fiscal_year_doc.year_start_date) &
			(Expense.expense_date <= fiscal_year_doc.year_end_date)
		)

	expense_result = expense_query.run(as_dict=True)
	expense_data = expense_result[0] if expense_result else {}

	# Calculate summary
	total_budgets = budget_data.get("total_budgets", 0)
	total_allocated = budget_data.get("total_allocated", 0) or 0
	total_spent = expense_data.get("total_spent", 0) or 0
	total_remaining = total_allocated - total_spent

	return {
		"total_budgets": total_budgets,
		"total_allocated": total_allocated,
		"total_spent": total_spent,
		"total_remaining": total_remaining,
		"utilization_percentage": (total_spent / total_allocated * 100) if total_allocated > 0 else 0
	}


def get_chart_data(data, filters):
	"""Generate chart data for departmental budget report"""
	if not data:
		return None

	# Extract department budget data
	departments = []
	allocated_amounts = []
	spent_amounts = []

	for row in data:
		if row.get("department_name") and row.get("allocated_amount"):
			departments.append(row["department_name"])
			allocated_amounts.append(row["allocated_amount"])
			spent_amounts.append(row.get("actual_expenses", 0))

	if not departments:
		return None

	return {
		"data": {
			"labels": departments,
			"datasets": [
				{
					"name": "Allocated",
					"values": allocated_amounts
				},
				{
					"name": "Spent",
					"values": spent_amounts
				}
			]
		},
		"type": "bar",
		"height": 300,
		"colors": ["#4CAF50", "#FF5722"]
	}


@frappe.whitelist()
def get_utilization_chart_data(data, filters):
	"""Generate budget utilization chart data"""
	if not data:
		return None

	# Parse JSON data if it's a string
	import json
	if isinstance(data, str):
		try:
			data = json.loads(data)
		except:
			return None

	if not isinstance(data, list):
		return None

	departments = []
	utilization_rates = []

	for row in data:
		if not isinstance(row, dict):
			continue

		if row.get("department_name") and row.get("utilization_percentage") is not None:
			departments.append(row["department_name"])
			# Convert utilization percentage to float
			try:
				utilization = float(row.get("utilization_percentage", 0) or 0)
			except (ValueError, TypeError):
				utilization = 0
			utilization_rates.append(utilization)

	return {
		"data": {
			"labels": departments,
			"datasets": [{
				"values": utilization_rates
			}]
		},
		"type": "bar",
		"height": 300,
		"colors": ["#2196F3"]
	}


@frappe.whitelist()
def get_department_comparison_chart(data, filters):
	"""Generate department comparison pie chart"""
	if not data:
		return None

	# Parse JSON data if it's a string
	import json
	if isinstance(data, str):
		try:
			data = json.loads(data)
		except:
			return None

	if not isinstance(data, list):
		return None

	departments = []
	allocated_amounts = []

	for row in data:
		if not isinstance(row, dict):
			continue

		# Convert allocated amount to float
		try:
			allocated_amount = float(row.get("allocated_amount", 0) or 0)
		except (ValueError, TypeError):
			allocated_amount = 0

		if row.get("department_name") and allocated_amount > 0:
			departments.append(row["department_name"])
			allocated_amounts.append(allocated_amount)

	return {
		"data": {
			"labels": departments,
			"datasets": [{
				"values": allocated_amounts
			}]
		},
		"type": "pie",
		"height": 300,
		"colors": ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#795548"]
	}


@frappe.whitelist()
def get_budget_status_breakdown(data, filters):
	"""Generate budget status breakdown chart"""
	if not data:
		return None

	# Parse JSON data if it's a string
	import json
	if isinstance(data, str):
		try:
			data = json.loads(data)
		except:
			return None

	if not isinstance(data, list):
		return None

	status_counts = {}
	status_amounts = {}

	for row in data:
		if not isinstance(row, dict):
			continue

		status = row.get("status", "Unknown")
		# Convert amount to float, handling empty strings and None values
		try:
			amount = float(row.get("allocated_amount", 0) or 0)
		except (ValueError, TypeError):
			amount = 0

		if status not in status_counts:
			status_counts[status] = 0
			status_amounts[status] = 0

		status_counts[status] += 1
		status_amounts[status] += amount

	return {
		"data": {
			"labels": list(status_amounts.keys()),
			"datasets": [{
				"values": list(status_amounts.values())
			}]
		},
		"type": "donut",
		"height": 300,
		"colors": ["#4CAF50", "#2196F3", "#FF9800", "#F44336", "#9E9E9E"]
	}
