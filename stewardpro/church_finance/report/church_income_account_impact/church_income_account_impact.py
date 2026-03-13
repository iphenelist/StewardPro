# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from stewardpro.church_finance.doctype.church_account.church_account import _get_all_leaf_balances


ACCOUNT_IMPACT_ROWS = [
	{
		"account": "Tithe Income",
		"component": _("Tithe"),
		"fieldname": "tithe",
		"destination": _("Conference"),
		"share_rule": _("100% posted"),
		"explanation": _("All submitted tithe is credited to this income account before remittance."),
	},
	{
		"account": "Regular Offering Income",
		"component": _("Regular Offering"),
		"fieldname": "offering_local_amount",
		"destination": _("Local Church"),
		"share_rule": _("42% local share"),
		"explanation": _("Only the local church share of regular offering is posted here."),
	},
	{
		"account": "Building Fund Income",
		"component": _("Building Fund"),
		"fieldname": "church_building_fund",
		"destination": _("Local Church"),
		"share_rule": _("100% retained locally"),
		"explanation": _("Building fund receipts stay with the local church and increase this account."),
	},
	{
		"account": "Camp Meeting Income",
		"component": _("Camp Meeting"),
		"fieldname": "camp_meeting",
		"destination": _("Conference"),
		"share_rule": _("100% posted"),
		"explanation": _("Camp meeting receipts are recognized here before conference remittance."),
	},
]


def execute(filters=None):
	filters = frappe._dict(filters or {})
	leaf_balances = _get_all_leaf_balances()
	data = get_data(filters, leaf_balances)
	message = _(
		"Regular Offering Income reflects only the 42% local church share. "
		"The conference share remains visible on Tithe and Offering entries but is not posted to this income account."
	)
	return get_columns(), data, message, get_chart(data), get_report_summary(data)


def get_columns():
	return [
		{"fieldname": "account", "label": _("Income Account"), "fieldtype": "Link", "options": "Church Account", "width": 180},
		{"fieldname": "component", "label": _("Giving Component"), "fieldtype": "Data", "width": 150},
		{"fieldname": "destination", "label": _("Destination"), "fieldtype": "Data", "width": 120},
		{"fieldname": "share_rule", "label": _("Posting Rule"), "fieldtype": "Data", "width": 140},
		{"fieldname": "entry_count", "label": _("Entries"), "fieldtype": "Int", "width": 75},
		{"fieldname": "amount_posted", "label": _("Amount Posted"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "current_balance", "label": _("Current Balance"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "last_entry_date", "label": _("Last Entry"), "fieldtype": "Date", "width": 100},
		{"fieldname": "explanation", "label": _("Explanation"), "fieldtype": "Data", "width": 280},
	]


def get_data(filters, leaf_balances):
	data = []
	for row_meta in ACCOUNT_IMPACT_ROWS:
		if filters.get("account") and filters.account != row_meta["account"]:
			continue
		if filters.get("destination") and filters.destination != row_meta["destination"]:
			continue

		aggregate = get_aggregate(row_meta["fieldname"], filters)
		amount_posted = flt(aggregate.amount_posted)
		if not filters.get("show_zero_accounts") and not amount_posted:
			continue

		data.append(
			{
				"account": row_meta["account"],
				"component": row_meta["component"],
				"destination": row_meta["destination"],
				"share_rule": row_meta["share_rule"],
				"entry_count": aggregate.entry_count or 0,
				"amount_posted": amount_posted,
				"current_balance": flt(leaf_balances.get(row_meta["account"], 0)),
				"last_entry_date": aggregate.last_entry_date,
				"explanation": row_meta["explanation"],
			}
		)

	data.sort(key=lambda row: row["amount_posted"], reverse=True)
	return data


def get_aggregate(fieldname, filters):
	conditions = ["docstatus = 1"]
	values = {}

	if filters.get("from_date"):
		conditions.append("entry_date >= %(from_date)s")
		values["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("entry_date <= %(to_date)s")
		values["to_date"] = filters.to_date

	if filters.get("member"):
		conditions.append("member = %(member)s")
		values["member"] = filters.member

	if filters.get("payment_method"):
		conditions.append("payment_method = %(payment_method)s")
		values["payment_method"] = filters.payment_method

	return frappe.db.sql(
		f"""
		SELECT
			COUNT(CASE WHEN IFNULL(`{fieldname}`, 0) > 0 THEN 1 END) AS entry_count,
			SUM(`{fieldname}`) AS amount_posted,
			MAX(CASE WHEN IFNULL(`{fieldname}`, 0) > 0 THEN entry_date END) AS last_entry_date
		FROM `tabTithe and Offering Entry`
		WHERE {' AND '.join(conditions)}
		""",
		values,
		as_dict=True,
	)[0]


def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [row["account"] for row in data],
			"datasets": [{"name": _("Posted Income"), "values": [flt(row["amount_posted"]) for row in data]}],
		},
		"type": "donut",
		"colors": ["#0d5c63", "#83b8be", "#cea75d", "#173337"],
	}


def get_report_summary(data):
	if not data:
		return None

	total_posted = sum(flt(row["amount_posted"]) for row in data)
	local_total = sum(flt(row["amount_posted"]) for row in data if row["destination"] == _("Local Church"))
	conference_total = sum(flt(row["amount_posted"]) for row in data if row["destination"] == _("Conference"))
	total_balance = sum(flt(row["current_balance"]) for row in data)

	return [
		{"value": total_posted, "indicator": "Blue", "label": _("Posted to Income Accounts"), "datatype": "Currency"},
		{"value": local_total, "indicator": "Green", "label": _("Local Church Income"), "datatype": "Currency"},
		{"value": conference_total, "indicator": "Orange", "label": _("Conference-Routed Income"), "datatype": "Currency"},
		{"value": total_balance, "indicator": "Purple", "label": _("Current Income Balances"), "datatype": "Currency"},
	]
