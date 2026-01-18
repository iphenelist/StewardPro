# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate
from frappe.query_builder.functions import Sum


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
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
			"label": _("Current Month"),
			"fieldname": "current_month",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Previous Month"),
			"fieldname": "previous_month",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Year to Date"),
			"fieldname": "year_to_date",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Previous Year"),
			"fieldname": "previous_year",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("% Change (Month)"),
			"fieldname": "month_change",
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"label": _("% Change (Year)"),
			"fieldname": "year_change",
			"fieldtype": "Percent",
			"width": 120
		}
	]


def get_data(filters):
	from frappe.utils import add_months, get_first_day, get_last_day
	
	# Date calculations
	today = getdate()
	current_month_start = get_first_day(today)
	current_month_end = get_last_day(today)
	
	previous_month_start = get_first_day(add_months(today, -1))
	previous_month_end = get_last_day(add_months(today, -1))
	
	year_start = getdate(f"{today.year}-01-01")
	previous_year_start = getdate(f"{today.year - 1}-01-01")
	previous_year_end = getdate(f"{today.year - 1}-12-31")
	
	data = []
	
	# Income Section
	data.append({
		"category": "<b>INCOME</b>",
		"current_month": "",
		"previous_month": "",
		"year_to_date": "",
		"previous_year": "",
		"month_change": "",
		"year_change": ""
	})
	
	# Tithes
	tithe_data = get_tithe_data(current_month_start, current_month_end, 
								previous_month_start, previous_month_end,
								year_start, today, previous_year_start, previous_year_end)
	data.append(tithe_data)
	
	# Offerings
	offering_data = get_offering_data(current_month_start, current_month_end,
									  previous_month_start, previous_month_end,
									  year_start, today, previous_year_start, previous_year_end)
	data.append(offering_data)
	
	# Special Offerings
	special_data = get_special_offerings_data(current_month_start, current_month_end,
											  previous_month_start, previous_month_end,
											  year_start, today, previous_year_start, previous_year_end)
	data.append(special_data)

	# Department Income
	dept_income_data = get_department_income_data(current_month_start, current_month_end,
												  previous_month_start, previous_month_end,
												  year_start, today, previous_year_start, previous_year_end)
	data.extend(dept_income_data)

	# Total Income
	total_income = calculate_total_income(data)
	data.append(total_income)
	
	# Expenses Section
	data.append({
		"category": "",
		"current_month": "",
		"previous_month": "",
		"year_to_date": "",
		"previous_year": "",
		"month_change": "",
		"year_change": ""
	})
	
	data.append({
		"category": "<b>EXPENSES</b>",
		"current_month": "",
		"previous_month": "",
		"year_to_date": "",
		"previous_year": "",
		"month_change": "",
		"year_change": ""
	})
	
	# Department Expenses
	expense_data = get_expense_data(current_month_start, current_month_end,
									previous_month_start, previous_month_end,
									year_start, today, previous_year_start, previous_year_end)
	data.extend(expense_data)

	return data


def get_tithe_data(cm_start, cm_end, pm_start, pm_end, yt_start, yt_end, py_start, py_end):
	tithes_table = frappe.qb.DocType("Tithes and Offerings")

	# Current month
	current_month = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.tithe_amount))
		.where(
			(tithes_table.date >= cm_start) &
			(tithes_table.date <= cm_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Previous month
	previous_month = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.tithe_amount))
		.where(
			(tithes_table.date >= pm_start) &
			(tithes_table.date <= pm_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Year to date
	year_to_date = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.tithe_amount))
		.where(
			(tithes_table.date >= yt_start) &
			(tithes_table.date <= yt_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Previous year
	previous_year = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.tithe_amount))
		.where(
			(tithes_table.date >= py_start) &
			(tithes_table.date <= py_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	month_change = calculate_percentage_change(current_month, previous_month)
	year_change = calculate_percentage_change(year_to_date, previous_year)

	return {
		"category": "Tithes",
		"current_month": current_month,
		"previous_month": previous_month,
		"year_to_date": year_to_date,
		"previous_year": previous_year,
		"month_change": month_change,
		"year_change": year_change
	}


def get_offering_data(cm_start, cm_end, pm_start, pm_end, yt_start, yt_end, py_start, py_end):
	tithes_table = frappe.qb.DocType("Tithes and Offerings")

	# Current month
	current_month = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.offering_amount))
		.where(
			(tithes_table.date >= cm_start) &
			(tithes_table.date <= cm_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Previous month
	previous_month = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.offering_amount))
		.where(
			(tithes_table.date >= pm_start) &
			(tithes_table.date <= pm_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Year to date
	year_to_date = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.offering_amount))
		.where(
			(tithes_table.date >= yt_start) &
			(tithes_table.date <= yt_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Previous year
	previous_year = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.offering_amount))
		.where(
			(tithes_table.date >= py_start) &
			(tithes_table.date <= py_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	month_change = calculate_percentage_change(current_month, previous_month)
	year_change = calculate_percentage_change(year_to_date, previous_year)

	return {
		"category": "Regular Offerings",
		"current_month": current_month,
		"previous_month": previous_month,
		"year_to_date": year_to_date,
		"previous_year": previous_year,
		"month_change": month_change,
		"year_change": year_change
	}


def get_special_offerings_data(cm_start, cm_end, pm_start, pm_end, yt_start, yt_end, py_start, py_end):
	tithes_table = frappe.qb.DocType("Tithes and Offerings")

	# Current month
	current_month = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.campmeeting_offering + tithes_table.church_building_offering))
		.where(
			(tithes_table.date >= cm_start) &
			(tithes_table.date <= cm_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Previous month
	previous_month = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.campmeeting_offering + tithes_table.church_building_offering))
		.where(
			(tithes_table.date >= pm_start) &
			(tithes_table.date <= pm_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Year to date
	year_to_date = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.campmeeting_offering + tithes_table.church_building_offering))
		.where(
			(tithes_table.date >= yt_start) &
			(tithes_table.date <= yt_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	# Previous year
	previous_year = (
		frappe.qb.from_(tithes_table)
		.select(Sum(tithes_table.campmeeting_offering + tithes_table.church_building_offering))
		.where(
			(tithes_table.date >= py_start) &
			(tithes_table.date <= py_end) &
			(tithes_table.docstatus == 1)
		)
	).run()[0][0] or 0

	month_change = calculate_percentage_change(current_month, previous_month)
	year_change = calculate_percentage_change(year_to_date, previous_year)

	return {
		"category": "Special Offerings",
		"current_month": current_month,
		"previous_month": previous_month,
		"year_to_date": year_to_date,
		"previous_year": previous_year,
		"month_change": month_change,
		"year_change": year_change
	}


def get_department_income_data(cm_start, cm_end, pm_start, pm_end, yt_start, yt_end, py_start, py_end):
	income_table = frappe.qb.DocType("Department Income")

	# Get departments with income
	departments = (
		frappe.qb.from_(income_table)
		.select(income_table.department)
		.distinct()
		.where(income_table.docstatus == 1)
		.orderby(income_table.department)
	).run()

	data = []
	for dept in departments:
		dept_name = dept[0]

		# Current month
		current_month = (
			frappe.qb.from_(income_table)
			.select(Sum(income_table.amount))
			.where(
				(income_table.date >= cm_start) &
				(income_table.date <= cm_end) &
				(income_table.department == dept_name) &
				(income_table.docstatus == 1)
			)
		).run()[0][0] or 0

		# Previous month
		previous_month = (
			frappe.qb.from_(income_table)
			.select(Sum(income_table.amount))
			.where(
				(income_table.date >= pm_start) &
				(income_table.date <= pm_end) &
				(income_table.department == dept_name) &
				(income_table.docstatus == 1)
			)
		).run()[0][0] or 0

		# Year to date
		year_to_date = (
			frappe.qb.from_(income_table)
			.select(Sum(income_table.amount))
			.where(
				(income_table.date >= yt_start) &
				(income_table.date <= yt_end) &
				(income_table.department == dept_name) &
				(income_table.docstatus == 1)
			)
		).run()[0][0] or 0

		# Previous year
		previous_year = (
			frappe.qb.from_(income_table)
			.select(Sum(income_table.amount))
			.where(
				(income_table.date >= py_start) &
				(income_table.date <= py_end) &
				(income_table.department == dept_name) &
				(income_table.docstatus == 1)
			)
		).run()[0][0] or 0

		month_change = calculate_percentage_change(current_month, previous_month)
		year_change = calculate_percentage_change(year_to_date, previous_year)

		data.append({
			"category": f"{dept_name} Income",
			"current_month": current_month,
			"previous_month": previous_month,
			"year_to_date": year_to_date,
			"previous_year": previous_year,
			"month_change": month_change,
			"year_change": year_change
		})

	return data


def get_expense_data(cm_start, cm_end, pm_start, pm_end, yt_start, yt_end, py_start, py_end):
	expense_table = frappe.qb.DocType("Department Expense")

	# Get expenses by department
	departments = (
		frappe.qb.from_(expense_table)
		.select(expense_table.department)
		.distinct()
		.where(expense_table.docstatus == 1)
		.orderby(expense_table.department)
	).run()

	data = []
	for dept in departments:
		dept_name = dept[0]

		# Current month
		current_month = (
			frappe.qb.from_(expense_table)
			.select(Sum(expense_table.total_amount))
			.where(
				(expense_table.expense_date >= cm_start) &
				(expense_table.expense_date <= cm_end) &
				(expense_table.department == dept_name) &
				(expense_table.docstatus == 1)
			)
		).run()[0][0] or 0

		# Previous month
		previous_month = (
			frappe.qb.from_(expense_table)
			.select(Sum(expense_table.total_amount))
			.where(
				(expense_table.expense_date >= pm_start) &
				(expense_table.expense_date <= pm_end) &
				(expense_table.department == dept_name) &
				(expense_table.docstatus == 1)
			)
		).run()[0][0] or 0

		# Year to date
		year_to_date = (
			frappe.qb.from_(expense_table)
			.select(Sum(expense_table.total_amount))
			.where(
				(expense_table.expense_date >= yt_start) &
				(expense_table.expense_date <= yt_end) &
				(expense_table.department == dept_name) &
				(expense_table.docstatus == 1)
			)
		).run()[0][0] or 0

		# Previous year
		previous_year = (
			frappe.qb.from_(expense_table)
			.select(Sum(expense_table.total_amount))
			.where(
				(expense_table.expense_date >= py_start) &
				(expense_table.expense_date <= py_end) &
				(expense_table.department == dept_name) &
				(expense_table.docstatus == 1)
			)
		).run()[0][0] or 0

		month_change = calculate_percentage_change(current_month, previous_month)
		year_change = calculate_percentage_change(year_to_date, previous_year)

		data.append({
			"category": f"{dept_name} Expenses",
			"current_month": current_month,
			"previous_month": previous_month,
			"year_to_date": year_to_date,
			"previous_year": previous_year,
			"month_change": month_change,
			"year_change": year_change
		})

	return data


def calculate_total_income(data):
	# Calculate totals from income items (skip headers)
	income_items = [item for item in data if item.get("category") and
					not item["category"].startswith("<b>") and
					(item["category"] in ["Tithes", "Regular Offerings", "Special Offerings"] or
					 item["category"].endswith(" Income"))]

	current_month = sum(flt(item.get("current_month", 0)) for item in income_items)
	previous_month = sum(flt(item.get("previous_month", 0)) for item in income_items)
	year_to_date = sum(flt(item.get("year_to_date", 0)) for item in income_items)
	previous_year = sum(flt(item.get("previous_year", 0)) for item in income_items)

	month_change = calculate_percentage_change(current_month, previous_month)
	year_change = calculate_percentage_change(year_to_date, previous_year)

	return {
		"category": "<b>TOTAL INCOME</b>",
		"current_month": current_month,
		"previous_month": previous_month,
		"year_to_date": year_to_date,
		"previous_year": previous_year,
		"month_change": month_change,
		"year_change": year_change
	}


def calculate_percentage_change(current, previous):
	if not previous:
		return 0
	return ((current - previous) / previous) * 100


def get_chart_data(data, filters):
	"""Generate chart data for financial summary"""
	if not data:
		return None

	# Extract income and expense data
	income_data = []
	expense_data = []

	for row in data:
		category = row.get("category", "")
		if not category or category.startswith("<b>") or not category.strip():
			continue

		current_month = row.get("current_month", 0)
		year_to_date = row.get("year_to_date", 0)

		if category in ["Tithes", "Regular Offerings", "Special Offerings"]:
			income_data.append({
				"category": category,
				"current_month": current_month,
				"year_to_date": year_to_date
			})
		elif "Expenses" in category:
			expense_data.append({
				"category": category,
				"current_month": current_month,
				"year_to_date": year_to_date
			})

	# Create chart data for income vs expenses comparison
	income_total = sum(item["current_month"] for item in income_data)
	expense_total = sum(item["current_month"] for item in expense_data)

	return {
		"data": {
			"labels": ["Income", "Expenses"],
			"datasets": [{
				"values": [income_total, expense_total]
			}]
		},
		"type": "pie",
		"height": 300,
		"colors": ["#4CAF50", "#F44336"]
	}


@frappe.whitelist()
def get_income_breakdown_chart(data, filters):
	"""Generate income breakdown chart data"""
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

	income_categories = []
	income_values = []

	for row in data:
		if not isinstance(row, dict):
			continue

		category = row.get("category", "")
		if category in ["Tithes", "Regular Offerings", "Special Offerings"]:
			income_categories.append(category)
			# Convert to float, handling empty strings and None values
			try:
				value = float(row.get("current_month", 0) or 0)
			except (ValueError, TypeError):
				value = 0
			income_values.append(value)

	return {
		"data": {
			"labels": income_categories,
			"datasets": [{
				"values": income_values
			}]
		},
		"type": "donut",
		"height": 300,
		"colors": ["#2E7D32", "#1976D2", "#F57C00"]
	}


@frappe.whitelist()
def get_expense_breakdown_chart(data, filters):
	"""Generate expense breakdown chart data"""
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

	expense_categories = []
	expense_values = []

	for row in data:
		if not isinstance(row, dict):
			continue

		category = row.get("category", "")
		if "Expenses" in category:
			expense_categories.append(category.replace(" Expenses", ""))
			# Convert to float, handling empty strings and None values
			try:
				value = float(row.get("current_month", 0) or 0)
			except (ValueError, TypeError):
				value = 0
			expense_values.append(value)

	return {
		"data": {
			"labels": expense_categories,
			"datasets": [{
				"values": expense_values
			}]
		},
		"type": "bar",
		"height": 300,
		"colors": ["#D32F2F", "#7B1FA2", "#F57C00", "#388E3C"]
	}


@frappe.whitelist()
def get_trend_comparison_chart(data, filters):
	"""Generate trend comparison chart data"""
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
	current_month_values = []
	previous_month_values = []
	ytd_values = []

	for row in data:
		if not isinstance(row, dict):
			continue

		category = row.get("category", "")
		if category in ["Tithes", "Regular Offerings", "Special Offerings"]:
			categories.append(category)
			# Convert to float, handling empty strings and None values
			try:
				current_value = float(row.get("current_month", 0) or 0)
			except (ValueError, TypeError):
				current_value = 0
			current_month_values.append(current_value)

			# Convert previous month value
			try:
				previous_value = float(row.get("previous_month", 0) or 0)
			except (ValueError, TypeError):
				previous_value = 0
			previous_month_values.append(previous_value)

			# Convert YTD value
			try:
				ytd_value = float(row.get("year_to_date", 0) or 0)
			except (ValueError, TypeError):
				ytd_value = 0
			ytd_values.append(ytd_value)

	return {
		"data": {
			"labels": categories,
			"datasets": [
				{
					"name": "Current Month",
					"values": current_month_values
				},
				{
					"name": "Previous Month",
					"values": previous_month_values
				},
				{
					"name": "Year to Date",
					"values": ytd_values
				}
			]
		},
		"type": "bar",
		"height": 350,
		"colors": ["#4CAF50", "#FF9800", "#2196F3"]
	}
