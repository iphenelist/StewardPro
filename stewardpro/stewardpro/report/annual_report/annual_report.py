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

	chart = get_chart_data(data, filters)
	return columns, data, None, chart


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
	
	# Expenses Section
	data.append({
		"category": "<b>OUTGOING</b>",
		"amount": "",
		"percentage": "",
		"previous_year_amount": "",
		"change_amount": "",
		"change_percentage": ""
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
	net_balance = total_income - current_data.get("total_expenses", 0)
	previous_net = previous_total_income - previous_data.get("total_expenses", 0)
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
	# Create date range for the year
	year_start = getdate(f"{year}-01-01")
	year_end = getdate(f"{year}-12-31")

	contrib_data = {}
	expense_data = {}

	# Get contributions data
	try:
		TithesOfferings = DocType("Tithes and Offerings")
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
	except Exception:
		contrib_data = {}

	# Get expenses data (only if Department Expense DocType exists)
	try:
		if frappe.db.exists("DocType", "Department Expense"):
			Expense = DocType("Department Expense")
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
	except Exception:
		expense_data = {}

	# Combine all data
	return {
		"total_tithes": flt(contrib_data.get("total_tithes", 0)),
		"total_offerings": flt(contrib_data.get("total_offerings", 0)),
		"total_camp_meeting": flt(contrib_data.get("total_camp_meeting", 0)),
		"total_building": flt(contrib_data.get("total_building", 0)),
		"total_expenses": flt(expense_data.get("total_expenses", 0))
	}


def get_chart_data(data, filters):
	"""Generate chart data for annual report"""
	if not data:
		return None

	# Extract income categories for chart
	income_categories = []
	income_amounts = []
	previous_year_amounts = []

	for row in data:
		category = row.get("category", "")
		if category and not category.startswith("<b>") and category.strip():
			if any(keyword in category.upper() for keyword in ["TITHE", "OFFERING", "INCOME"]):
				income_categories.append(category)
				income_amounts.append(row.get("amount", 0))
				previous_year_amounts.append(row.get("previous_year_amount", 0))

	if not income_categories:
		return None

	return {
		"data": {
			"labels": income_categories,
			"datasets": [
				{
					"name": "Current Year",
					"values": income_amounts
				},
				{
					"name": "Previous Year",
					"values": previous_year_amounts
				}
			]
		},
		"type": "bar",
		"height": 300,
		"colors": ["#2E7D32", "#1976D2"]
	}


def parse_amount(value):
	"""Parse amount from potentially HTML-formatted string"""
	import re
	if value is None or value == "":
		return 0
	if isinstance(value, (int, float)):
		return float(value)
	# Remove HTML tags
	value = re.sub(r'<[^>]+>', '', str(value))
	# Remove currency symbols and formatting
	value = re.sub(r'[^\d.-]', '', value)
	try:
		return float(value) if value else 0
	except (ValueError, TypeError):
		return 0


@frappe.whitelist()
def get_category_breakdown_chart(data, filters):
	"""Generate category breakdown pie chart"""
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

	categories = []
	amounts = []

	for row in data:
		if not isinstance(row, dict):
			continue

		category = row.get("category", "")
		amount = parse_amount(row.get("amount"))

		if (category and not category.startswith("<b>") and
			category.strip() and amount > 0 and
			any(keyword in category.upper() for keyword in ["TITHE", "OFFERING", "CAMP", "BUILDING"])):
			categories.append(category)
			amounts.append(amount)

	if not categories:
		return None

	return {
		"data": {
			"labels": categories,
			"datasets": [{
				"values": amounts
			}]
		},
		"type": "pie",
		"height": 300,
		"colors": ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]
	}


@frappe.whitelist()
def get_year_comparison_chart(data, filters):
	"""Generate year-over-year comparison chart"""
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

	categories = []
	current_amounts = []
	previous_amounts = []
	changes = []

	for row in data:
		if not isinstance(row, dict):
			continue

		category = row.get("category", "")

		# Convert amounts to float, handling empty strings and None values
		try:
			current = float(row.get("amount", 0) or 0)
		except (ValueError, TypeError):
			current = 0

		try:
			previous = float(row.get("previous_year_amount", 0) or 0)
		except (ValueError, TypeError):
			previous = 0

		if (category and not category.startswith("<b>") and
			category.strip() and (current > 0 or previous > 0)):
			categories.append(category)
			current_amounts.append(current)
			previous_amounts.append(previous)

			# Calculate percentage change
			if previous > 0:
				change = ((current - previous) / previous) * 100
			else:
				change = 100 if current > 0 else 0
			changes.append(change)

	return {
		"data": {
			"labels": categories,
			"datasets": [
				{
					"name": "Current Year",
					"values": current_amounts
				},
				{
					"name": "Previous Year",
					"values": previous_amounts
				}
			]
		},
		"type": "bar",
		"height": 350,
		"colors": ["#4CAF50", "#FF5722"]
	}


@frappe.whitelist()
def get_financial_health_metrics(data, filters):
	"""Calculate financial health metrics"""
	if not data:
		return {}

	# Parse JSON data if it's a string
	import json
	if isinstance(data, str):
		try:
			data = json.loads(data)
		except:
			return {}

	if not isinstance(data, list):
		return {}

	total_income = 0
	total_expenses = 0
	previous_income = 0

	for row in data:
		if not isinstance(row, dict):
			continue

		category = row.get("category", "")
		current = parse_amount(row.get("amount"))
		previous = parse_amount(row.get("previous_year_amount"))

		if "INCOME" in category.upper() or any(keyword in category.upper() for keyword in ["TITHE", "OFFERING"]):
			total_income += current
			previous_income += previous
		elif "EXPENSE" in category.upper():
			total_expenses += current

	net_income = total_income - total_expenses
	income_growth = ((total_income - previous_income) / previous_income * 100) if previous_income > 0 else 0
	expense_ratio = (total_expenses / total_income * 100) if total_income > 0 else 0

	return {
		"total_income": total_income,
		"total_expenses": total_expenses,
		"net_income": net_income,
		"income_growth": income_growth,
		"expense_ratio": expense_ratio
	}


def calculate_percentage_change(current, previous):
	"""Calculate percentage change between two values"""
	if previous == 0:
		return 100 if current > 0 else 0

	return ((current - previous) / previous) * 100



