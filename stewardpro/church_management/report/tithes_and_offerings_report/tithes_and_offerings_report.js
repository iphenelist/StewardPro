// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Tithes and Offerings Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "member",
			"label": __("Member"),
			"fieldtype": "Link",
			"options": "Church Member"
		},
		{
			"fieldname": "payment_mode",
			"label": __("Payment Mode"),
			"fieldtype": "Select",
			"options": "\nCash\nMpesa\nBank Transfer\nOther"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "member_name" && data && data.member_name == "Anonymous") {
			value = `<span class="text-muted">${value}</span>`;
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom buttons
		report.page.add_inner_button(__("Export Summary"), function() {
			frappe.query_report.export_report();
		});
	}
};
