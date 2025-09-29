# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
from frappe.utils import flt, getdate


def execute(filters=None):
	if not filters:
		filters = {}
	
	columns = get_columns()
	data = get_data(filters)
	
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
			"label": _("Amount Sent"),
			"fieldname": "amount_sent",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Recipient"),
			"fieldname": "recipient",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Organization Type"),
			"fieldname": "organization_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Proof of Payment"),
			"fieldname": "reference_number",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Pending Balance"),
			"fieldname": "pending_balance",
			"fieldtype": "Currency",
			"width": 150
		}
	]


def get_data(filters):
	Remittance = DocType("Remittance")
	
	# Build main query
	query = (
		frappe.qb.from_(Remittance)
		.select(
			Remittance.remittance_date.as_("date"),
			Remittance.total_remittance_amount.as_("amount_sent"),
			Remittance.organization_name.as_("recipient"),
			Remittance.organization_type,
			Remittance.reference_number,
			Remittance.status
		)
		.where(Remittance.docstatus >= 0)
		.orderby(Remittance.remittance_date, order=frappe.qb.desc)
	)
	
	# Apply filters
	if filters.get("from_date"):
		query = query.where(Remittance.remittance_date >= getdate(filters.get("from_date")))

	if filters.get("to_date"):
		query = query.where(Remittance.remittance_date <= getdate(filters.get("to_date")))

	if filters.get("church"):
		query = query.where(Remittance.church == filters.get("church"))

	if filters.get("organization_type"):
		query = query.where(Remittance.organization_type == filters.get("organization_type"))

	if filters.get("status"):
		query = query.where(Remittance.status == filters.get("status"))

	if filters.get("payment_mode"):
		query = query.where(Remittance.payment_mode == filters.get("payment_mode"))
	
	data = query.run(as_dict=True)
	
	# Calculate pending balance for each remittance
	for row in data:
		row["pending_balance"] = calculate_pending_balance(row.get("date"), filters)
	
	return data


def calculate_pending_balance(remittance_date, filters):
	"""Calculate pending balance based on collections vs remittances up to a specific date"""
	TithesOfferings = DocType("Tithes and Offerings")
	Remittance = DocType("Remittance")
	
	# Get total collections up to remittance date
	collections_query = (
		frappe.qb.from_(TithesOfferings)
		.select(
			Sum(
				TithesOfferings.tithe_amount + 
				TithesOfferings.offering_to_field +
				TithesOfferings.campmeeting_offering +
				TithesOfferings.church_building_offering
			).as_("total_collections")
		)
		.where(TithesOfferings.docstatus == 1)
		.where(TithesOfferings.date <= remittance_date)
	)
	
	if filters.get("from_date"):
		collections_query = collections_query.where(TithesOfferings.date >= getdate(filters.get("from_date")))
	
	collections_result = collections_query.run(as_dict=True)
	total_collections = flt(collections_result[0]["total_collections"]) if collections_result else 0
	
	# Get total remittances up to remittance date
	remittances_query = (
		frappe.qb.from_(Remittance)
		.select(Sum(Remittance.total_remittance_amount).as_("total_remitted"))
		.where(Remittance.docstatus == 1)
		.where(Remittance.remittance_date <= remittance_date)
	)
	
	if filters.get("from_date"):
		remittances_query = remittances_query.where(Remittance.remittance_date >= getdate(filters.get("from_date")))
	
	remittances_result = remittances_query.run(as_dict=True)
	total_remitted = flt(remittances_result[0]["total_remitted"]) if remittances_result else 0
	
	return total_collections - total_remitted


@frappe.whitelist()
def get_pending_balance(filters=None):
	"""Get pending remittance balance summary"""
	if not filters:
		filters = {}

	if isinstance(filters, str):
		import json
		filters = json.loads(filters)

	try:
		TithesOfferings = DocType("Tithes and Offerings")
		Remittance = DocType("Remittance")

		# Get total collections that should be remitted
		collections_query = (
			frappe.qb.from_(TithesOfferings)
			.select(
				Sum(
					TithesOfferings.tithe_amount +
					TithesOfferings.offering_to_field +
					TithesOfferings.campmeeting_offering +
					TithesOfferings.church_building_offering
				).as_("total_collections")
			)
			.where(TithesOfferings.docstatus == 1)
		)

		# Apply date filters
		if filters.get("from_date"):
			collections_query = collections_query.where(TithesOfferings.date >= getdate(filters.get("from_date")))

		if filters.get("to_date"):
			collections_query = collections_query.where(TithesOfferings.date <= getdate(filters.get("to_date")))

		collections_result = collections_query.run(as_dict=True)
		total_to_remit = flt(collections_result[0]["total_collections"]) if collections_result else 0

		# Get total remittances sent
		remittances_query = (
			frappe.qb.from_(Remittance)
			.select(Sum(Remittance.total_remittance_amount).as_("total_remitted"))
			.where(Remittance.docstatus == 1)
		)

		# Apply date filters
		if filters.get("from_date"):
			remittances_query = remittances_query.where(Remittance.remittance_date >= getdate(filters.get("from_date")))

		if filters.get("to_date"):
			remittances_query = remittances_query.where(Remittance.remittance_date <= getdate(filters.get("to_date")))

		# Apply organization type filter
		if filters.get("organization_type"):
			remittances_query = remittances_query.where(Remittance.organization_type == filters.get("organization_type"))

		remittances_result = remittances_query.run(as_dict=True)
		total_remitted = flt(remittances_result[0]["total_remitted"]) if remittances_result else 0

		pending_balance = total_to_remit - total_remitted

		return {
			"total_to_remit": total_to_remit,
			"total_remitted": total_remitted,
			"pending_balance": pending_balance
		}

	except Exception as e:
		frappe.log_error(f"Error in get_pending_balance: {str(e)}")
		return {
			"total_to_remit": 0,
			"total_remitted": 0,
			"pending_balance": 0
		}
