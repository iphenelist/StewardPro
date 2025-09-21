# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
from frappe.utils import getdate, flt

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
			"label": _("Category"),
			"fieldname": "category",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Percentage of Total Income"),
			"fieldname": "percentage",
			"fieldtype": "Percent",
			"width": 150
		},
		{
			"label": _("Previous Year"),
			"fieldname": "previous_year_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Change"),
			"fieldname": "change_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Change %"),
			"fieldname": "change_percentage",
			"fieldtype": "Percent",
			"width": 100
		}
	]


def get_data(filters):
	year = int(filters.get("year", getdate().year))
	previous_year = year - 1

	# Get current year data
	current_data = get_year_data(year)

	# Get previous year data for comparison
	previous_data = get_year_data(previous_year)

	# Calculate total income for percentage calculations
	total_income = (
		current_data.get("total_tithes", 0) +
		current_data.get("total_offerings", 0) +
		current_data.get("total_camp_meeting", 0) +
		current_data.get("total_building", 0)
	)

	data = []

	# Ensure we have valid data structures
	if not isinstance(current_data, dict):
		current_data = {}
	if not isinstance(previous_data, dict):
		previous_data = {}
	
	# Income Section
	data.append({
		"category": "<b>INCOME</b>",
		"amount": "",
		"percentage": "",
		"previous_year_amount": "",
		"change_amount": "",
		"change_percentage": ""
	})
	
	# Tithes
	tithe_change = current_data.get("total_tithes", 0) - previous_data.get("total_tithes", 0)
	tithe_change_pct = calculate_percentage_change(current_data.get("total_tithes", 0), previous_data.get("total_tithes", 0))
	
	data.append({
		"category": "Total Tithes",
		"amount": current_data.get("total_tithes", 0),
		"percentage": (current_data.get("total_tithes", 0) / total_income * 100) if total_income > 0 else 0,
		"previous_year_amount": previous_data.get("total_tithes", 0),
		"change_amount": tithe_change,
		"change_percentage": tithe_change_pct
	})
	
	# Offerings
	offering_change = current_data.get("total_offerings", 0) - previous_data.get("total_offerings", 0)
	offering_change_pct = calculate_percentage_change(current_data.get("total_offerings", 0), previous_data.get("total_offerings", 0))
	
	data.append({
		"category": "Total Offerings",
		"amount": current_data.get("total_offerings", 0),
		"percentage": (current_data.get("total_offerings", 0) / total_income * 100) if total_income > 0 else 0,
		"previous_year_amount": previous_data.get("total_offerings", 0),
		"change_amount": offering_change,
		"change_percentage": offering_change_pct
	})
	
	# Camp Meeting Offerings
	camp_change = current_data.get("total_camp_meeting", 0) - previous_data.get("total_camp_meeting", 0)
	camp_change_pct = calculate_percentage_change(current_data.get("total_camp_meeting", 0), previous_data.get("total_camp_meeting", 0))
	
	data.append({
		"category": "Total Camp Meeting Offerings",
		"amount": current_data.get("total_camp_meeting", 0),
		"percentage": (current_data.get("total_camp_meeting", 0) / total_income * 100) if total_income > 0 else 0,
		"previous_year_amount": previous_data.get("total_camp_meeting", 0),
		"change_amount": camp_change,
		"change_percentage": camp_change_pct
	})
	
	# Building Offerings
	building_change = current_data.get("total_building", 0) - previous_data.get("total_building", 0)
	building_change_pct = calculate_percentage_change(current_data.get("total_building", 0), previous_data.get("total_building", 0))
	
	data.append({
		"category": "Total Building Offerings",
		"amount": current_data.get("total_building", 0),
		"percentage": (current_data.get("total_building", 0) / total_income * 100) if total_income > 0 else 0,
		"previous_year_amount": previous_data.get("total_building", 0),
		"change_amount": building_change,
		"change_percentage": building_change_pct
	})
	
	# Total Income
	income_change = total_income - (
		previous_data.get("total_tithes", 0) + 
		previous_data.get("total_offerings", 0) + 
		previous_data.get("total_camp_meeting", 0) + 
		previous_data.get("total_building", 0)
	)
	previous_total_income = (
		previous_data.get("total_tithes", 0) + 
		previous_data.get("total_offerings", 0) + 
		previous_data.get("total_camp_meeting", 0) + 
		previous_data.get("total_building", 0)
	)
	income_change_pct = calculate_percentage_change(total_income, previous_total_income)
	
	data.append({
		"category": "<b>TOTAL INCOME</b>",
		"amount": total_income,
		"percentage": 100,
		"previous_year_amount": previous_total_income,
		"change_amount": income_change,
		"change_percentage": income_change_pct
	})
	
	# Separator
	data.append({
		"category": "",
		"amount": "",
		"percentage": "",
		"previous_year_amount": "",
		"change_amount": "",
		"change_percentage": ""
	})
	
	# Remittances and Expenses Section
	data.append({
		"category": "<b>OUTGOING</b>",
		"amount": "",
		"percentage": "",
		"previous_year_amount": "",
		"change_amount": "",
		"change_percentage": ""
	})
	
	# Total Remitted
	remit_change = current_data.get("total_remitted", 0) - previous_data.get("total_remitted", 0)
	remit_change_pct = calculate_percentage_change(current_data.get("total_remitted", 0), previous_data.get("total_remitted", 0))
	
	data.append({
		"category": "Total Remitted",
		"amount": current_data.get("total_remitted", 0),
		"percentage": (current_data.get("total_remitted", 0) / total_income * 100) if total_income > 0 else 0,
		"previous_year_amount": previous_data.get("total_remitted", 0),
		"change_amount": remit_change,
		"change_percentage": remit_change_pct
	})
	
	# Total Expenses
	expense_change = current_data.get("total_expenses", 0) - previous_data.get("total_expenses", 0)
	expense_change_pct = calculate_percentage_change(current_data.get("total_expenses", 0), previous_data.get("total_expenses", 0))
	
	data.append({
		"category": "Total Expenses",
		"amount": current_data.get("total_expenses", 0),
		"percentage": (current_data.get("total_expenses", 0) / total_income * 100) if total_income > 0 else 0,
		"previous_year_amount": previous_data.get("total_expenses", 0),
		"change_amount": expense_change,
		"change_percentage": expense_change_pct
	})
	
	# Net Balance
	net_balance = total_income - current_data.get("total_remitted", 0) - current_data.get("total_expenses", 0)
	previous_net = previous_total_income - previous_data.get("total_remitted", 0) - previous_data.get("total_expenses", 0)
	net_change = net_balance - previous_net
	net_change_pct = calculate_percentage_change(net_balance, previous_net)
	
	data.append({
		"category": "<b>NET BALANCE</b>",
		"amount": net_balance,
		"percentage": (net_balance / total_income * 100) if total_income > 0 else 0,
		"previous_year_amount": previous_net,
		"change_amount": net_change,
		"change_percentage": net_change_pct
	})
	
	return data


def get_year_data(year):
	"""Get financial data for a specific year using Frappe QB"""
	TithesOfferings = DocType("Tithes and Offerings")
	Remittance = DocType("Remittance")
	Expense = DocType("Department Expense")

	# Create date range for the year
	year_start = getdate(f"{year}-01-01")
	year_end = getdate(f"{year}-12-31")

	# Get contributions data
	contributions_query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			Sum(TithesOfferings.tithe_amount).as_("total_tithes"),
			Sum(TithesOfferings.offering_amount).as_("total_offerings"),
			Sum(TithesOfferings.campmeeting_offering).as_("total_camp_meeting"),
			Sum(TithesOfferings.church_building_offering).as_("total_building")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.date >= year_start)
		.where(TithesOfferings.date <= year_end)
	)

	contributions = contributions_query.run(as_dict=True)
	contrib_data = contributions[0] if contributions else {}

	# Get remittances data
	remittances_query = (
		frappe.qb.from_(Remittance)
		.select(
			Sum(Remittance.total_remittance_amount).as_("total_remitted")
		)
		.where(Remittance.docstatus == 1)
		.where(Remittance.remittance_date >= year_start)
		.where(Remittance.remittance_date <= year_end)
	)

	remittances = remittances_query.run(as_dict=True)
	remit_data = remittances[0] if remittances else {}

	# Get expenses data
	expenses_query = (
		frappe.qb.from_(Expense)
		.select(
			Sum(Expense.total_amount).as_("total_expenses")
		)
		.where(Expense.docstatus == 1)
		.where(Expense.expense_date >= year_start)
		.where(Expense.expense_date <= year_end)
	)

	expenses = expenses_query.run(as_dict=True)
	expense_data = expenses[0] if expenses else {}

	# Combine all data
	return {
		"total_tithes": flt(contrib_data.get("total_tithes", 0)),
		"total_offerings": flt(contrib_data.get("total_offerings", 0)),
		"total_camp_meeting": flt(contrib_data.get("total_camp_meeting", 0)),
		"total_building": flt(contrib_data.get("total_building", 0)),
		"total_remitted": flt(remit_data.get("total_remitted", 0)),
		"total_expenses": flt(expense_data.get("total_expenses", 0))
	}


def calculate_percentage_change(current, previous):
	"""Calculate percentage change between two values"""
	if previous == 0:
		return 100 if current > 0 else 0

	return ((current - previous) / previous) * 100



