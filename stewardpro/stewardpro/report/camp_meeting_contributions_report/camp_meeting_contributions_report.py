# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count, Avg, Min, Max
from frappe.utils import getdate

# Define custom functions for date operations - commented out to avoid CustomFunction issues
# def Year(field):
# 	return frappe.qb.CustomFunction("YEAR", [field])

# def Month(field):
# 	return frappe.qb.CustomFunction("MONTH", [field])


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
			"label": _("Member"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "Member",
			"width": 200
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
			"label": _("Camp Meeting Offering"),
			"fieldname": "campmeeting_offering",
			"fieldtype": "Currency",
			"width": 180
		},
		{
			"label": _("Payment Mode"),
			"fieldname": "payment_mode",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Receipt Number"),
			"fieldname": "receipt_number",
			"fieldtype": "Data",
			"width": 120
		}
	]


def get_data(filters):
	TithesOfferings = DocType("Tithes and Offerings")
	Member = DocType("Member")
	
	# Build main query
	query = (
		frappe.qb.from_(TithesOfferings)
		.left_join(Member)
		.on(TithesOfferings.member == Member.name)
		.select(
			TithesOfferings.member,
			Member.full_name.as_("member_name"),
			TithesOfferings.date,
			TithesOfferings.campmeeting_offering,
			TithesOfferings.payment_mode,
			TithesOfferings.receipt_number
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.campmeeting_offering > 0)
		.orderby(TithesOfferings.date, order=frappe.qb.desc)
	)
	
	# Apply filters
	if filters.get("year"):
		year = int(filters.get("year"))
		year_start = getdate(f"{year}-01-01")
		year_end = getdate(f"{year}-12-31")
		query = query.where(
			(TithesOfferings.date >= year_start) &
			(TithesOfferings.date <= year_end)
		)
	
	if filters.get("from_date"):
		query = query.where(TithesOfferings.date >= getdate(filters.get("from_date")))
	
	if filters.get("to_date"):
		query = query.where(TithesOfferings.date <= getdate(filters.get("to_date")))
	
	if filters.get("member"):
		query = query.where(TithesOfferings.member == filters.get("member"))
	
	data = query.run(as_dict=True)
	
	# Handle anonymous contributions
	for row in data:
		if not row.get("member"):
			row["member"] = ""
			row["member_name"] = "Anonymous"
	
	return data

@frappe.whitelist()
def get_member_summary(filters=None):
	"""Get camp meeting contributions summary by member"""
	if not filters:
		filters = {}

	if isinstance(filters, str):
		import json
		filters = json.loads(filters)

	TithesOfferings = DocType("Tithes and Offerings")
	Member = DocType("Member")
	
	query = (
		frappe.qb.from_(TithesOfferings)
		.left_join(Member)
		.on(TithesOfferings.member == Member.name)
		.select(
			TithesOfferings.member,
			Member.full_name.as_("member_name"),
			Count(TithesOfferings.name).as_("contribution_count"),
			Sum(TithesOfferings.campmeeting_offering).as_("total_contribution"),
			Avg(TithesOfferings.campmeeting_offering).as_("avg_contribution"),
			Max(TithesOfferings.campmeeting_offering).as_("max_contribution")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.campmeeting_offering > 0)
		.groupby(TithesOfferings.member, Member.full_name)
		.orderby(Sum(TithesOfferings.campmeeting_offering), order=frappe.qb.desc)
	)
	
	# Apply filters
	if filters.get("year"):
		year = int(filters.get("year"))
		year_start = getdate(f"{year}-01-01")
		year_end = getdate(f"{year}-12-31")
		query = query.where(
			(TithesOfferings.date >= year_start) &
			(TithesOfferings.date <= year_end)
		)
	
	if filters.get("from_date"):
		query = query.where(TithesOfferings.date >= getdate(filters.get("from_date")))
	
	if filters.get("to_date"):
		query = query.where(TithesOfferings.date <= getdate(filters.get("to_date")))
	
	data = query.run(as_dict=True)
	
	# Handle anonymous contributions
	for row in data:
		if not row.get("member"):
			row["member"] = ""
			row["member_name"] = "Anonymous"
	
	return data


def get_yearly_summary(filters):
	"""Get camp meeting contributions summary by year - simplified version"""
	# Temporarily return empty data to avoid Year/Month function issues
	# TODO: Implement proper yearly grouping without SQL date functions
	return []


def get_monthly_summary(filters):
	"""Get camp meeting contributions summary by month - simplified version"""
	# Temporarily return empty data to avoid Year/Month function issues
	# TODO: Implement proper monthly grouping without SQL date functions
	return []


def get_top_contributors(filters, limit=10):
	"""Get top camp meeting contributors"""
	member_summary = get_member_summary(filters)
	return member_summary[:limit]


def get_contribution_statistics(filters):
	"""Get overall contribution statistics"""
	TithesOfferings = DocType("Tithes and Offerings")
	
	query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			Count(TithesOfferings.name).as_("total_contributions"),
			Sum(TithesOfferings.campmeeting_offering).as_("total_amount"),
			Avg(TithesOfferings.campmeeting_offering).as_("avg_contribution"),
			Min(TithesOfferings.campmeeting_offering).as_("min_contribution"),
			Max(TithesOfferings.campmeeting_offering).as_("max_contribution"),
			Count(TithesOfferings.member.distinct()).as_("unique_contributors")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.campmeeting_offering > 0)
	)
	
	# Apply filters
	if filters.get("year"):
		year = int(filters.get("year"))
		year_start = getdate(f"{year}-01-01")
		year_end = getdate(f"{year}-12-31")
		query = query.where(
			(TithesOfferings.date >= year_start) &
			(TithesOfferings.date <= year_end)
		)
	
	if filters.get("from_date"):
		query = query.where(TithesOfferings.date >= getdate(filters.get("from_date")))
	
	if filters.get("to_date"):
		query = query.where(TithesOfferings.date <= getdate(filters.get("to_date")))
	
	result = query.run(as_dict=True)
	return result[0] if result else {}
