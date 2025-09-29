# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Avg, Count, Max, Min, Sum
from frappe.utils import getdate, flt


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
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Contributor"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "Member",
			"width": 150
		},
		{
			"label": _("Contributor Name"),
			"fieldname": "member_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Amount"),
			"fieldname": "church_building_offering",
			"fieldtype": "Currency",
			"width": 120
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
		},
		{
			"label": _("Running Total"),
			"fieldname": "running_total",
			"fieldtype": "Currency",
			"width": 130
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
			TithesOfferings.date,
			TithesOfferings.member,
			Member.full_name.as_("member_name"),
			TithesOfferings.church_building_offering,
			TithesOfferings.payment_mode,
			TithesOfferings.receipt_number
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.church_building_offering > 0)
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
	
	if filters.get("contributor"):
		query = query.where(TithesOfferings.member == filters.get("contributor"))
	
	data = query.run(as_dict=True)
	
	# Calculate running total and handle anonymous contributions
	running_total = 0
	for row in data:
		if not row.get("member"):
			row["member"] = ""
			row["member_name"] = "Anonymous"
		
		running_total += flt(row.get("church_building_offering", 0))
		row["running_total"] = running_total
	
	return data


def get_contributor_summary(filters):
	"""Get building fund contributions summary by contributor"""
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
			Sum(TithesOfferings.church_building_offering).as_("total_contribution"),
			Avg(TithesOfferings.church_building_offering).as_("avg_contribution"),
			Max(TithesOfferings.church_building_offering).as_("max_contribution"),
			Min(TithesOfferings.date).as_("first_contribution_date"),
			Max(TithesOfferings.date).as_("last_contribution_date")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.church_building_offering > 0)
		.groupby(TithesOfferings.member, Member.full_name)
		.orderby(Sum(TithesOfferings.church_building_offering), order=frappe.qb.desc)
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


def get_monthly_summary(filters):
	"""Get building fund contributions summary by month - simplified version"""
	# Temporarily return empty data to avoid Year/Month function issues
	# TODO: Implement proper monthly grouping without SQL date functions
	return []


def get_project_progress(filters):
	"""Get building fund project progress"""
	TithesOfferings = DocType("Tithes and Offerings")
	
	# Get total contributions
	query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			Sum(TithesOfferings.church_building_offering).as_("total_raised"),
			Count(TithesOfferings.name).as_("total_contributions"),
			Count(TithesOfferings.member.distinct()).as_("total_contributors"),
			Min(TithesOfferings.date).as_("campaign_start"),
			Max(TithesOfferings.date).as_("last_contribution")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.church_building_offering > 0)
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


def get_contribution_trends(filters):
	"""Get contribution trends over time"""
	TithesOfferings = DocType("Tithes and Offerings")
	
	query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			TithesOfferings.date,
			TithesOfferings.church_building_offering,
			Sum(TithesOfferings.church_building_offering).over(
				order_by=TithesOfferings.date
			).as_("cumulative_total")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.church_building_offering > 0)
		.orderby(TithesOfferings.date)
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
	
	return query.run(as_dict=True)
