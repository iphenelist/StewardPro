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

	return columns, data


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
	Expense = DocType("Church Expense")

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
			.select(Sum(Expense.amount).as_("total_expenses"))
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
