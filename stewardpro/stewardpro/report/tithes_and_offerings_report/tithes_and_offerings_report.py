# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data, filters)

	return columns, data, None, chart


def get_columns():
	return [
		{
			"label": _("Member"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "Member",
			"width": 150
		},
		{
			"label": _("Member Name"),
			"fieldname": "member_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Tithe Amount"),
			"fieldname": "tithe_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Offering Amount"),
			"fieldname": "offering_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Camp Meeting Offering"),
			"fieldname": "campmeeting_offering",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Building Offering"),
			"fieldname": "church_building_offering",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Total Amount"),
			"fieldname": "total_amount",
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
		}
	]


def get_data(filters):
	conditions = ["t.docstatus = 1"]
	values = []

	if filters.get("from_date"):
		conditions.append("t.date >= %s")
		values.append(getdate(filters.get("from_date")))

	if filters.get("to_date"):
		conditions.append("t.date <= %s")
		values.append(getdate(filters.get("to_date")))

	if filters.get("member"):
		conditions.append("t.member = %s")
		values.append(filters.get("member"))

	if filters.get("payment_mode"):
		conditions.append("t.payment_mode = %s")
		values.append(filters.get("payment_mode"))

	query = f"""
		SELECT
			t.member,
			COALESCE(m.full_name, 'Anonymous') as member_name,
			t.date,
			t.tithe_amount,
			t.offering_amount,
			t.campmeeting_offering,
			t.church_building_offering,
			t.total_amount,
			t.payment_mode,
			t.receipt_number
		FROM `tabTithes and Offerings` t
		LEFT JOIN `tabMember` m ON t.member = m.name
		WHERE {' AND '.join(conditions)}
		ORDER BY t.date DESC
	"""

	data = frappe.db.sql(query, values, as_dict=True)

	# Handle anonymous contributions
	for row in data:
		if not row.get("member"):
			row["member"] = ""
			row["member_name"] = "Anonymous"

	return data


def get_chart_data(data, filters):
	"""Generate chart data for the report"""
	if not data:
		return None

	# Group by month for trend chart
	monthly_data = {}
	member_totals = {}
	payment_mode_totals = {}

	for row in data:
		# Monthly trends
		month = row.get("date").strftime("%Y-%m") if row.get("date") else "Unknown"
		if month not in monthly_data:
			monthly_data[month] = {
				"tithe": 0,
				"offering": 0,
				"special": 0,
				"total": 0
			}

		monthly_data[month]["tithe"] += row.get("tithe_amount", 0)
		monthly_data[month]["offering"] += row.get("offering_amount", 0)
		monthly_data[month]["special"] += (
			row.get("campmeeting_offering", 0) +
			row.get("church_building_offering", 0)
		)
		monthly_data[month]["total"] += row.get("total_amount", 0)

		# Member contributions
		member = row.get("member_name", "Anonymous")
		if member not in member_totals:
			member_totals[member] = 0
		member_totals[member] += row.get("total_amount", 0)

		# Payment mode breakdown
		payment_mode = row.get("payment_mode", "Unknown")
		if payment_mode not in payment_mode_totals:
			payment_mode_totals[payment_mode] = 0
		payment_mode_totals[payment_mode] += row.get("total_amount", 0)

	months = sorted(monthly_data.keys())

	# Get top 10 contributors
	top_members = sorted(member_totals.items(), key=lambda x: x[1], reverse=True)[:10]

	return {
		"data": {
			"labels": months,
			"datasets": [
				{
					"name": "Tithes",
					"values": [monthly_data[month]["tithe"] for month in months]
				},
				{
					"name": "Offerings",
					"values": [monthly_data[month]["offering"] for month in months]
				},
				{
					"name": "Special Offerings",
					"values": [monthly_data[month]["special"] for month in months]
				}
			]
		},
		"type": "bar",
		"height": 300,
		"colors": ["#2E7D32", "#1976D2", "#F57C00"]
	}


@frappe.whitelist()
def get_member_chart_data(data, filters):
	"""Generate member contribution chart data"""
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

	member_totals = {}
	for row in data:
		if not isinstance(row, dict):
			continue

		member = row.get("member_name", "Anonymous")
		if member not in member_totals:
			member_totals[member] = 0

		# Convert amount to float, handling empty strings and None values
		try:
			amount = float(row.get("total_amount", 0) or 0)
		except (ValueError, TypeError):
			amount = 0
		member_totals[member] += amount

	# Get top 10 contributors
	top_members = sorted(member_totals.items(), key=lambda x: x[1], reverse=True)[:10]

	return {
		"data": {
			"labels": [member[0] for member in top_members],
			"datasets": [{
				"values": [member[1] for member in top_members]
			}]
		},
		"type": "pie",
		"height": 300
	}


@frappe.whitelist()
def get_payment_mode_chart_data(data, filters):
	"""Generate payment mode breakdown chart data"""
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

	payment_mode_totals = {}
	for row in data:
		if not isinstance(row, dict):
			continue

		payment_mode = row.get("payment_mode", "Unknown")
		if payment_mode not in payment_mode_totals:
			payment_mode_totals[payment_mode] = 0

		# Convert amount to float, handling empty strings and None values
		try:
			amount = float(row.get("total_amount", 0) or 0)
		except (ValueError, TypeError):
			amount = 0
		payment_mode_totals[payment_mode] += amount

	return {
		"data": {
			"labels": list(payment_mode_totals.keys()),
			"datasets": [{
				"values": list(payment_mode_totals.values())
			}]
		},
		"type": "donut",
		"height": 300
	}
