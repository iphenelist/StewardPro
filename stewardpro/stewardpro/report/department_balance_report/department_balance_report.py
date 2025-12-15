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
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 150
		},
		{
			"label": _("Department Code"),
			"fieldname": "department_code",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Total Income"),
			"fieldname": "total_income",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Expenses"),
			"fieldname": "total_expenses",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Currency",
			"width": 120
		}
	]


def get_data(filters):
	# Get all departments
	departments = frappe.get_all(
		"Department",
		filters={"is_active": 1},
		fields=["name", "department_name", "department_code"]
	)
	
	data = []
	
	for dept in departments:
		# Get total income
		income_query = frappe.qb.from_(DocType("Department Income")).select(
			Sum(DocType("Department Income").amount).as_("total")
		).where(DocType("Department Income").department == dept.name).where(
			DocType("Department Income").docstatus == 1
		)
		
		# Get total expenses
		expense_query = frappe.qb.from_(DocType("Department Expense")).select(
			Sum(DocType("Department Expense").total_amount).as_("total")
		).where(DocType("Department Expense").department == dept.name).where(
			DocType("Department Expense").docstatus == 1
		)
		
		# Apply date filters if provided
		if filters.get("from_date"):
			income_query = income_query.where(
				DocType("Department Income").date >= getdate(filters.get("from_date"))
			)
			expense_query = expense_query.where(
				DocType("Department Expense").expense_date >= getdate(filters.get("from_date"))
			)
		
		if filters.get("to_date"):
			income_query = income_query.where(
				DocType("Department Income").date <= getdate(filters.get("to_date"))
			)
			expense_query = expense_query.where(
				DocType("Department Expense").expense_date <= getdate(filters.get("to_date"))
			)
		
		income_result = income_query.run(as_dict=True)
		expense_result = expense_query.run(as_dict=True)
		
		total_income = income_result[0].total or 0 if income_result else 0
		total_expenses = expense_result[0].total or 0 if expense_result else 0
		balance = total_income - total_expenses
		
		data.append({
			"department": dept.name,
			"department_code": dept.department_code,
			"total_income": total_income,
			"total_expenses": total_expenses,
			"balance": balance
		})
	
	return data

