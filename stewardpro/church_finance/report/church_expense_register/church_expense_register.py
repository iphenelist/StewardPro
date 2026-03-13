# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{"fieldname": "expense_date", "label": _("Date"), "fieldtype": "Date", "width": 95},
		{"fieldname": "name", "label": _("Expense No"), "fieldtype": "Link", "options": "Church Expense", "width": 150},
		{"fieldname": "department", "label": _("Department"), "fieldtype": "Link", "options": "Church Department", "width": 170},
		{"fieldname": "account", "label": _("Expense Account"), "fieldtype": "Link", "options": "Church Account", "width": 190},
		{"fieldname": "paid_from", "label": _("Paid From"), "fieldtype": "Link", "options": "Church Account", "width": 170},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "approval_status", "label": _("Approval"), "fieldtype": "Data", "width": 130},
		{"fieldname": "payment_method", "label": _("Payment Method"), "fieldtype": "Data", "width": 120},
		{"fieldname": "requested_by", "label": _("Requested By"), "fieldtype": "Link", "options": "Church Member", "width": 150},
		{"fieldname": "approved_by", "label": _("Approved By"), "fieldtype": "Link", "options": "User", "width": 130},
		{"fieldname": "description", "label": _("Description"), "fieldtype": "Data", "width": 240},
	]


def get_conditions(filters):
	conditions = ["docstatus < 2"]
	values = {}

	for fieldname in ("department", "account", "paid_from", "approval_status", "payment_method"):
		if filters.get(fieldname):
			conditions.append(f"{fieldname} = %({fieldname})s")
			values[fieldname] = filters[fieldname]

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
			expense_date,
			name,
			department,
			account,
			paid_from,
			amount,
			approval_status,
			payment_method,
			requested_by,
			approved_by,
			description
		FROM `tabChurch Expense`
		WHERE {conditions}
		ORDER BY expense_date DESC, modified DESC
		""",
		values,
		as_dict=True,
	)


def get_chart(data):
	if not data:
		return None

	department_totals = {}
	for row in data:
		key = row.department or _("Unassigned")
		department_totals[key] = department_totals.get(key, 0) + flt(row.amount)

	labels = list(department_totals.keys())[:8]
	values = [department_totals[label] for label in labels]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Spend"), "values": values}],
		},
		"type": "bar",
		"colors": ["#0d5c63"],
	}


def get_report_summary(data):
	if not data:
		return None

	total_amount = sum(flt(row.amount) for row in data)
	approved_amount = sum(flt(row.amount) for row in data if row.approval_status == "Approved")
	pending_amount = sum(
		flt(row.amount) for row in data if row.approval_status in {"Draft", "Pending Approval"}
	)
	active_departments = len({row.department for row in data if row.department})

	return [
		{"value": total_amount, "indicator": "Blue", "label": _("Tracked Spend"), "datatype": "Currency"},
		{"value": approved_amount, "indicator": "Green", "label": _("Approved Spend"), "datatype": "Currency"},
		{"value": pending_amount, "indicator": "Orange", "label": _("Awaiting Action"), "datatype": "Currency"},
		{"value": active_departments, "indicator": "Purple", "label": _("Departments Active"), "datatype": "Int"},
	]
