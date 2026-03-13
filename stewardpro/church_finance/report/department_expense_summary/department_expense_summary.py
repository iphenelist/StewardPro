# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{"fieldname": "department", "label": _("Department"), "fieldtype": "Link", "options": "Church Department", "width": 180},
		{"fieldname": "account", "label": _("Expense Account"), "fieldtype": "Link", "options": "Church Account", "width": 200},
		{"fieldname": "expense_count", "label": _("Entries"), "fieldtype": "Int", "width": 80},
		{"fieldname": "total_amount", "label": _("Total Amount"), "fieldtype": "Currency", "width": 135},
		{"fieldname": "average_amount", "label": _("Average"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "largest_expense", "label": _("Largest Expense"), "fieldtype": "Currency", "width": 135},
		{"fieldname": "last_expense_date", "label": _("Last Expense Date"), "fieldtype": "Date", "width": 120},
	]


def get_conditions(filters):
	conditions = ["docstatus < 2"]
	values = {}

	if filters.get("only_submitted"):
		conditions = ["docstatus = 1"]

	if filters.get("department"):
		conditions.append("department = %(department)s")
		values["department"] = filters["department"]

	if filters.get("from_date"):
		conditions.append("expense_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("expense_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	return " AND ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	return frappe.db.sql(
		f"""
		SELECT
			department,
			account,
			COUNT(name) AS expense_count,
			SUM(amount) AS total_amount,
			AVG(amount) AS average_amount,
			MAX(amount) AS largest_expense,
			MAX(expense_date) AS last_expense_date
		FROM `tabChurch Expense`
		WHERE {conditions}
		GROUP BY department, account
		ORDER BY total_amount DESC, department
		""",
		values,
		as_dict=True,
	)


def get_chart(data):
	if not data:
		return None

	department_totals = {}
	for row in data:
		department_totals.setdefault(row.department, 0)
		department_totals[row.department] += row.total_amount

	return {
		"data": {
			"labels": list(department_totals.keys())[:8],
			"datasets": [{"name": _("Approved Spend"), "values": list(department_totals.values())[:8]}],
		},
		"type": "donut",
		"colors": ["#0d5c63", "#83b8be", "#cea75d", "#173337", "#5a8b8f"],
	}


def get_report_summary(data):
	if not data:
		return None

	total_departments = len({row.department for row in data if row.department})
	total_amount = sum(row.total_amount for row in data)
	largest_department_row = max(data, key=lambda row: row.total_amount)

	return [
		{"value": total_departments, "indicator": "Blue", "label": _("Departments Reporting"), "datatype": "Int"},
		{"value": total_amount, "indicator": "Green", "label": _("Department Spend"), "datatype": "Currency"},
		{"value": largest_department_row.department, "indicator": "Purple", "label": _("Top Spending Department"), "datatype": "Data"},
		{"value": largest_department_row.total_amount, "indicator": "Orange", "label": _("Top Department Spend"), "datatype": "Currency"},
	]
