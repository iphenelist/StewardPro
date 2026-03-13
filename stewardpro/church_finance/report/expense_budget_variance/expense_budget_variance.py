# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from stewardpro.church_finance.doctype.church_budget.church_budget import refresh_expense_actuals


def execute(filters=None):
	filters = frappe._dict(filters or {})
	refresh_expense_actuals()
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{"fieldname": "budget_name", "label": _("Budget"), "fieldtype": "Link", "options": "Church Budget", "width": 180},
		{"fieldname": "department", "label": _("Department"), "fieldtype": "Link", "options": "Church Department", "width": 170},
		{"fieldname": "account", "label": _("Expense Account"), "fieldtype": "Link", "options": "Church Account", "width": 190},
		{"fieldname": "budgeted_amount", "label": _("Budgeted"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "actual_amount", "label": _("Actual"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "variance", "label": _("Variance"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "budget_status", "label": _("Budget Status"), "fieldtype": "Data", "width": 125},
	]


def get_conditions(filters):
	conditions = ["budget.docstatus < 2", "item.parentfield = 'expense_items'"]
	values = {}

	if filters.get("budget"):
		conditions.append("budget.name = %(budget)s")
		values["budget"] = filters["budget"]

	if filters.get("budget_year"):
		conditions.append("budget.budget_year = %(budget_year)s")
		values["budget_year"] = filters["budget_year"]

	if filters.get("budget_period"):
		conditions.append("budget.budget_period = %(budget_period)s")
		values["budget_period"] = filters["budget_period"]

	if filters.get("department"):
		conditions.append("request.department = %(department)s")
		values["department"] = filters["department"]

	if filters.get("show_only_over_budget"):
		conditions.append("item.variance < 0")

	return " AND ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	rows = frappe.db.sql(
		f"""
		SELECT
			budget.name AS budget_name,
			request.department,
			item.account,
			item.budgeted_amount,
			item.actual_amount,
			item.variance
		FROM `tabChurch Budget` budget
		JOIN `tabBudget Line Item` item
			ON item.parent = budget.name
		LEFT JOIN `tabDepartment Budget Request` request
			ON request.name = budget.department_budget_request
		WHERE {conditions}
		ORDER BY item.variance ASC, item.actual_amount DESC
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		if flt(row.variance) < 0:
			row.budget_status = _("Over Budget")
		elif flt(row.actual_amount) == 0:
			row.budget_status = _("Unused")
		elif flt(row.variance) == 0:
			row.budget_status = _("Fully Used")
		else:
			row.budget_status = _("Within Budget")

	return rows


def get_chart(data):
	if not data:
		return None

	top_rows = sorted(data, key=lambda row: abs(flt(row.variance)), reverse=True)[:8]
	return {
		"data": {
			"labels": [row.account for row in top_rows],
			"datasets": [
				{"name": _("Budgeted"), "values": [flt(row.budgeted_amount) for row in top_rows]},
				{"name": _("Actual"), "values": [flt(row.actual_amount) for row in top_rows]},
			],
		},
		"type": "bar",
		"colors": ["#83b8be", "#0d5c63"],
	}


def get_report_summary(data):
	if not data:
		return None

	total_budgeted = sum(flt(row.budgeted_amount) for row in data)
	total_actual = sum(flt(row.actual_amount) for row in data)
	total_remaining = sum(max(flt(row.variance), 0) for row in data)
	total_overrun = abs(sum(min(flt(row.variance), 0) for row in data))

	return [
		{"value": total_budgeted, "indicator": "Blue", "label": _("Budgeted Spend"), "datatype": "Currency"},
		{"value": total_actual, "indicator": "Green", "label": _("Actual Spend"), "datatype": "Currency"},
		{"value": total_remaining, "indicator": "Orange", "label": _("Remaining Budget"), "datatype": "Currency"},
		{"value": total_overrun, "indicator": "Red", "label": _("Overrun Risk"), "datatype": "Currency"},
	]
