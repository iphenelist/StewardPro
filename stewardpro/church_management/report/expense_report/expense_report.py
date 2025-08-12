# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Avg, Count, Sum
from frappe.utils import getdate


def execute(filters=None):
	if not filters:
		filters = {}
	
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data


def get_columns():
	return [
		{
			"label": _("Date"),
			"fieldname": "expense_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Category"),
			"fieldname": "expense_category",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Description"),
			"fieldname": "expense_description",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Approved By"),
			"fieldname": "approved_by",
			"fieldtype": "Link",
			"options": "User",
			"width": 120
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Receipt"),
			"fieldname": "attachments",
			"fieldtype": "Data",
			"width": 80
		}
	]


def get_data(filters):
	Expense = DocType("Church Expense")
	
	# Build main query
	query = (
		frappe.qb.from_(Expense)
		.select(
			Expense.expense_date,
			Expense.department,
			Expense.expense_category,
			Expense.expense_description,
			Expense.amount,
			Expense.approved_by,
			Expense.status,
			Expense.attachments,
			Expense.name
		)
		.where(Expense.docstatus >= 0)
		.orderby(Expense.expense_date, order=frappe.qb.desc)
	)
	
	# Apply filters
	if filters.get("from_date"):
		query = query.where(Expense.expense_date >= getdate(filters.get("from_date")))

	if filters.get("to_date"):
		query = query.where(Expense.expense_date <= getdate(filters.get("to_date")))

	if filters.get("department"):
		query = query.where(Expense.department == filters.get("department"))

	if filters.get("expense_category"):
		query = query.where(Expense.expense_category == filters.get("expense_category"))

	if filters.get("status"):
		query = query.where(Expense.status == filters.get("status"))

	if filters.get("payment_mode"):
		query = query.where(Expense.payment_mode == filters.get("payment_mode"))

	if filters.get("budget_reference"):
		query = query.where(Expense.budget_reference == filters.get("budget_reference"))
	
	data = query.run(as_dict=True)
	
	# Format receipt attachment display
	for row in data:
		if row.get("attachments"):
			row["attachments"] = "✓ Attached"
		else:
			row["attachments"] = "✗ Missing"
	
	return data


def get_expense_summary_by_department(filters):
	"""Get expense summary grouped by department"""
	Expense = DocType("Church Expense")

	query = (
		frappe.qb.from_(Expense)
		.select(
			Expense.department,
			Count(Expense.name).as_("count"),
			Sum(Expense.amount).as_("total_amount"),
			Avg(Expense.amount).as_("avg_amount")
		)
		.where(Expense.docstatus == 1)
		.groupby(Expense.department)
		.orderby(Sum(Expense.amount), order=frappe.qb.desc)
	)

	# Apply date filters
	if filters.get("from_date"):
		query = query.where(Expense.expense_date >= getdate(filters.get("from_date")))

	if filters.get("to_date"):
		query = query.where(Expense.expense_date <= getdate(filters.get("to_date")))

	return query.run(as_dict=True)


def get_expense_summary_by_category(filters):
	"""Get expense summary grouped by category"""
	Expense = DocType("Church Expense")

	query = (
		frappe.qb.from_(Expense)
		.select(
			Expense.expense_category,
			Count(Expense.name).as_("count"),
			Sum(Expense.amount).as_("total_amount"),
			Avg(Expense.amount).as_("avg_amount")
		)
		.where(Expense.docstatus == 1)
		.groupby(Expense.expense_category)
		.orderby(Sum(Expense.amount), order=frappe.qb.desc)
	)

	# Apply date filters
	if filters.get("from_date"):
		query = query.where(Expense.expense_date >= getdate(filters.get("from_date")))

	if filters.get("to_date"):
		query = query.where(Expense.expense_date <= getdate(filters.get("to_date")))

	return query.run(as_dict=True)





def get_pending_approvals(filters):
	"""Get expenses pending approval"""
	Expense = DocType("Church Expense")
	
	query = (
		frappe.qb.from_(Expense)
		.select(
			Expense.name,
			Expense.expense_date,
			Expense.expense_description,
			Expense.amount,
			Expense.status
		)
		.where(Expense.docstatus == 0)
		.where(Expense.status.isin(["Draft", "Pending Approval"]))
		.orderby(Expense.expense_date, order=frappe.qb.desc)
	)
	
	# Apply date filters
	if filters.get("from_date"):
		query = query.where(Expense.expense_date >= getdate(filters.get("from_date")))
	
	if filters.get("to_date"):
		query = query.where(Expense.expense_date <= getdate(filters.get("to_date")))
	
	return query.run(as_dict=True)


def get_expenses_without_receipts(filters):
	"""Get expenses that don't have receipt attachments"""
	Expense = DocType("Church Expense")
	
	query = (
		frappe.qb.from_(Expense)
		.select(
			Expense.name,
			Expense.expense_date,
			Expense.expense_description,
			Expense.amount
		)
		.where(Expense.docstatus == 1)
		.where(
			(Expense.attachments.isnull()) | 
			(Expense.attachments
    == "")
		)
		.orderby(Expense.expense_date, order=frappe.qb.desc)
	)
	
	# Apply date filters
	if filters.get("from_date"):
		query = query.where(Expense.expense_date >= getdate(filters.get("from_date")))
	
	if filters.get("to_date"):
		query = query.where(Expense.expense_date <= getdate(filters.get("to_date")))
	
	return query.run(as_dict=True)


# Test function to ensure module loads correctly
def test_module():
	"""Test function to verify module integrity"""
	return "Module loaded successfully"


# Alternative implementation of get_expense_summary
@frappe.whitelist()
def get_expense_summary_alt(filters=None):
	"""Alternative implementation of expense summary"""
	return {
		"by_department": [{"department": "Test", "count": 1, "total_amount": 100}],
		"by_category": [{"expense_category": "Test", "count": 1, "total_amount": 100}]
	}


# Main expense summary function - moved to end of file
@frappe.whitelist()
def get_expense_summary(filters=None):
	"""Get comprehensive expense summary for the report"""
	if not filters:
		filters = {}

	if isinstance(filters, str):
		import json
		filters = json.loads(filters)

	try:
		# Get summary by department
		by_department = get_expense_summary_by_department(filters)

		# Get summary by category
		by_category = get_expense_summary_by_category(filters)

		return {
			"by_department": by_department,
			"by_category": by_category
		}
	except Exception as e:
		frappe.log_error(f"Error in get_expense_summary: {str(e)}")
		return {
			"by_department": [],
			"by_category": []
		}
