// Copyright (c) 2025, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Department Income Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 0
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 0
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"reqd": 0
		},
		{
			"fieldname": "income_type",
			"label": __("Income Type"),
			"fieldtype": "Select",
			"options": "\nTithe\nOffering\nDonation\nFund Raising\nGrant\nOther",
			"reqd": 0
		},
		{
			"fieldname": "payment_mode",
			"label": __("Payment Mode"),
			"fieldtype": "Select",
			"options": "\nCash\nCheque\nBank Transfer\nMpesa\nCredit Card\nOther",
			"reqd": 0
		}
	]
};

