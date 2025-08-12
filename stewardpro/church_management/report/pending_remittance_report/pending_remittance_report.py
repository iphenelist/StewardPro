# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day

# Define custom functions for date operations - using date range filtering instead
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
			"label": _("Period"),
			"fieldname": "period",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Total Tithes Collected"),
			"fieldname": "total_tithes",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Total Offerings to Field"),
			"fieldname": "total_offerings_to_field",
			"fieldtype": "Currency",
			"width": 170
		},
		{
			"label": _("Total Special Offerings"),
			"fieldname": "total_special_offerings",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": _("Total to Remit"),
			"fieldname": "total_to_remit",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Amount Remitted"),
			"fieldname": "amount_remitted",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Amount Pending"),
			"fieldname": "amount_pending",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Pending %"),
			"fieldname": "pending_percentage",
			"fieldtype": "Percent",
			"width": 100
		}
	]


def get_data(filters):
	# Get period range
	from_date = getdate(filters.get("from_date")) if filters.get("from_date") else add_months(getdate(), -12)
	to_date = getdate(filters.get("to_date")) if filters.get("to_date") else getdate()
	
	data = []
	
	# Generate monthly periods
	current_date = get_first_day(from_date)
	
	while current_date <= to_date:
		period_start = current_date
		period_end = get_last_day(current_date)
		
		# Get contributions for this period
		contributions = get_period_contributions(period_start, period_end)
		
		# Get remittances for this period
		remittances = get_period_remittances(period_start, period_end)
		
		# Calculate totals
		total_tithes = flt(contributions.get("total_tithes", 0))
		total_offerings_to_field = flt(contributions.get("total_offerings_to_field", 0))
		total_special_offerings = flt(contributions.get("total_special_offerings", 0))
		total_to_remit = total_tithes + total_offerings_to_field + total_special_offerings
		
		amount_remitted = flt(remittances.get("total_remitted", 0))
		amount_pending = total_to_remit - amount_remitted
		
		pending_percentage = 0
		if total_to_remit > 0:
			pending_percentage = (amount_pending / total_to_remit) * 100
		
		# Only include periods with data
		if total_to_remit > 0 or amount_remitted > 0:
			data.append({
				"period": period_start.strftime("%B %Y"),
				"total_tithes": total_tithes,
				"total_offerings_to_field": total_offerings_to_field,
				"total_special_offerings": total_special_offerings,
				"total_to_remit": total_to_remit,
				"amount_remitted": amount_remitted,
				"amount_pending": amount_pending,
				"pending_percentage": pending_percentage
			})
		
		# Move to next month
		current_date = add_months(current_date, 1)
	
	return data


def get_period_contributions(period_start, period_end):
	"""Get contributions for a specific period"""
	TithesOfferings = DocType("Tithes and Offerings")
	
	query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			Sum(TithesOfferings.tithe_amount).as_("total_tithes"),
			Sum(TithesOfferings.offering_to_field).as_("total_offerings_to_field"),
			Sum(
				TithesOfferings.campmeeting_offering +
				TithesOfferings.church_building_offering
			).as_("total_special_offerings")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.date >= period_start)
		.where(TithesOfferings.date <= period_end)
	)
	
	result = query.run(as_dict=True)
	return result[0] if result else {}


def get_period_remittances(period_start, period_end):
	"""Get remittances for a specific period"""
	Remittance = DocType("Remittance")
	
	query = (
		frappe.qb.from_(Remittance)
		.select(
			Sum(Remittance.total_remittance_amount).as_("total_remitted")
		)
		.where(Remittance.docstatus == 1)
		.where(Remittance.remittance_date >= period_start)
		.where(Remittance.remittance_date <= period_end)
	)
	
	result = query.run(as_dict=True)
	return result[0] if result else {}


def get_overall_summary(filters):
	"""Get overall summary of pending remittances"""
	from_date = getdate(filters.get("from_date")) if filters.get("from_date") else add_months(getdate(), -12)
	to_date = getdate(filters.get("to_date")) if filters.get("to_date") else getdate()
	
	TithesOfferings = DocType("Tithes and Offerings")
	Remittance = DocType("Remittance")
	
	# Get total contributions
	contributions_query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			Sum(TithesOfferings.tithe_amount).as_("total_tithes"),
			Sum(TithesOfferings.offering_to_field).as_("total_offerings_to_field"),
			Sum(
				TithesOfferings.campmeeting_offering +
				TithesOfferings.church_building_offering
			).as_("total_special_offerings")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.date >= from_date)
		.where(TithesOfferings.date <= to_date)
	)
	
	contributions = contributions_query.run(as_dict=True)
	contrib_data = contributions[0] if contributions else {}
	
	total_to_remit = (
		flt(contrib_data.get("total_tithes", 0)) + 
		flt(contrib_data.get("total_offerings_to_field", 0)) + 
		flt(contrib_data.get("total_special_offerings", 0))
	)
	
	# Get total remittances
	remittances_query = (
		frappe.qb.from_(Remittance)
		.select(
			Sum(Remittance.total_remittance_amount).as_("total_remitted")
		)
		.where(Remittance.docstatus == 1)
		.where(Remittance.remittance_date >= from_date)
		.where(Remittance.remittance_date <= to_date)
	)
	
	remittances = remittances_query.run(as_dict=True)
	total_remitted = flt(remittances[0].get("total_remitted", 0)) if remittances else 0
	
	total_pending = total_to_remit - total_remitted
	pending_percentage = (total_pending / total_to_remit * 100) if total_to_remit > 0 else 0
	
	return {
		"total_tithes": contrib_data.get("total_tithes", 0),
		"total_offerings_to_field": contrib_data.get("total_offerings_to_field", 0),
		"total_special_offerings": contrib_data.get("total_special_offerings", 0),
		"total_to_remit": total_to_remit,
		"total_remitted": total_remitted,
		"total_pending": total_pending,
		"pending_percentage": pending_percentage
	}


def get_overdue_remittances(filters):
	"""Get remittances that are overdue (more than 30 days)"""
	from datetime import datetime, timedelta

	cutoff_date = datetime.now().date() - timedelta(days=30)

	TithesOfferings = DocType("Tithes and Offerings")

	# Get all collections older than 30 days
	collections_query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			TithesOfferings.date,
			Sum(
				TithesOfferings.tithe_amount +
				TithesOfferings.offering_to_field +
				TithesOfferings.campmeeting_offering +
				TithesOfferings.church_building_offering
			).as_("total_collected")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.date <= cutoff_date)
		.groupby(TithesOfferings.date)
		.orderby(TithesOfferings.date)
	)

	collections = collections_query.run(as_dict=True)

	# Group by month and calculate overdue amounts
	monthly_collections = {}
	for collection in collections:
		date = collection.get("date")
		if date:
			month_key = f"{date.year}-{date.month:02d}"
			if month_key not in monthly_collections:
				monthly_collections[month_key] = {
					"year": date.year,
					"month": date.month,
					"total_collected": 0,
					"period_start": get_first_day(date),
					"period_end": get_last_day(date)
				}
			monthly_collections[month_key]["total_collected"] += flt(collection.get("total_collected", 0))

	overdue_data = []
	for month_key, collection_data in monthly_collections.items():
		period_start = collection_data["period_start"]
		period_end = collection_data["period_end"]

		# Check remittances for this period
		remittances = get_period_remittances(period_start, period_end)
		total_remitted = flt(remittances.get("total_remitted", 0))
		total_collected = collection_data["total_collected"]

		if total_collected > total_remitted:
			overdue_amount = total_collected - total_remitted
			overdue_data.append({
				"period": period_start.strftime("%B %Y"),
				"total_collected": total_collected,
				"total_remitted": total_remitted,
				"overdue_amount": overdue_amount,
				"days_overdue": (datetime.now().date() - period_end).days
			})

	return overdue_data


def get_remittance_compliance_score(filters):
	"""Calculate remittance compliance score"""
	data = get_data(filters)
	
	if not data:
		return 100  # Perfect score if no data
	
	total_periods = len(data)
	compliant_periods = 0
	
	for period in data:
		pending_percentage = period.get("pending_percentage", 0)
		if pending_percentage <= 10:  # Consider 10% or less as compliant
			compliant_periods += 1
	
	compliance_score = (compliant_periods / total_periods * 100) if total_periods > 0 else 100
	
	return {
		"compliance_score": compliance_score,
		"total_periods": total_periods,
		"compliant_periods": compliant_periods,
		"non_compliant_periods": total_periods - compliant_periods
	}
