# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data


def get_columns():
	return [
		{
			"label": _("Member"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "Church Member",
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
		LEFT JOIN `tabChurch Member` m ON t.member = m.name
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
	
	# Group by month for chart
	monthly_data = {}
	for row in data:
		month = row.get("date").strftime("%Y-%m") if row.get("date") else "Unknown"
		if month not in monthly_data:
			monthly_data[month] = {
				"tithe": 0,
				"offering": 0,
				"special": 0
			}
		
		monthly_data[month]["tithe"] += row.get("tithe_amount", 0)
		monthly_data[month]["offering"] += row.get("offering_amount", 0)
		monthly_data[month]["special"] += (
			row.get("campmeeting_offering", 0) + 
			row.get("church_building_offering", 0)
		)
	
	months = sorted(monthly_data.keys())
	
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
		"height": 300
	}
