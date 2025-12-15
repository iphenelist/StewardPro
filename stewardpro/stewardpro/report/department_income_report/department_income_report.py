# Copyright (c) 2025, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
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
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 120
		},
		{
			"label": _("Department Code"),
			"fieldname": "department_code",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Income Type"),
			"fieldname": "income_type",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Payment Mode"),
			"fieldname": "payment_mode",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Receipt Number"),
			"fieldname": "receipt_number",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Text",
			"width": 150
		}
	]


def get_data(filters):
	Income = DocType("Department Income")

	# Build main query
	query = (
		frappe.qb.from_(Income)
		.select(
			Income.name,
			Income.date,
			Income.department,
			Income.department_code,
			Income.income_type,
			Income.amount,
			Income.payment_mode,
			Income.receipt_number,
			Income.description
		)
		.where(Income.docstatus == 1)
		.orderby(Income.date, order=frappe.qb.desc)
	)
	
	# Apply filters
	if filters.get("from_date"):
		query = query.where(Income.date >= getdate(filters.get("from_date")))

	if filters.get("to_date"):
		query = query.where(Income.date <= getdate(filters.get("to_date")))

	if filters.get("department"):
		query = query.where(Income.department == filters.get("department"))

	if filters.get("income_type"):
		query = query.where(Income.income_type == filters.get("income_type"))

	if filters.get("payment_mode"):
		query = query.where(Income.payment_mode == filters.get("payment_mode"))
	
	data = query.run(as_dict=True)
	
	return data


@frappe.whitelist()
def get_income_summary(filters=None):
	"""Get comprehensive income summary for the report"""
	if not filters:
		filters = {}

	if isinstance(filters, str):
		import json
		filters = json.loads(filters)

	try:
		# Get summary by department
		by_department = get_income_summary_by_department(filters)
		# Get summary by income type
		by_type = get_income_summary_by_type(filters)

		return {
			"by_department": by_department,
			"by_type": by_type
		}
	except Exception as e:
		frappe.log_error(f"Error in get_income_summary: {str(e)}")
		return {
			"by_department": [],
			"by_type": []
		}


def get_income_summary_by_department(filters):
	"""Get income summary grouped by department"""
	Income = DocType("Department Income")

	query = (
		frappe.qb.from_(Income)
		.select(
			Income.department,
			Sum(Income.amount).as_("total_amount")
		)
		.where(Income.docstatus == 1)
		.groupby(Income.department)
		.orderby(Sum(Income.amount), order=frappe.qb.desc)
	)

	# Apply date filters
	if filters.get("from_date"):
		query = query.where(Income.date >= getdate(filters.get("from_date")))

	if filters.get("to_date"):
		query = query.where(Income.date <= getdate(filters.get("to_date")))

	return query.run(as_dict=True)


def get_income_summary_by_type(filters):
	"""Get income summary grouped by income type"""
	Income = DocType("Department Income")

	query = (
		frappe.qb.from_(Income)
		.select(
			Income.income_type,
			Sum(Income.amount).as_("total_amount")
		)
		.where(Income.docstatus == 1)
		.groupby(Income.income_type)
		.orderby(Sum(Income.amount), order=frappe.qb.desc)
	)

	# Apply date filters
	if filters.get("from_date"):
		query = query.where(Income.date >= getdate(filters.get("from_date")))

	if filters.get("to_date"):
		query = query.where(Income.date <= getdate(filters.get("to_date")))

	return query.run(as_dict=True)

