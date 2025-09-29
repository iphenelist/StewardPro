// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Remittance Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
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
			"fieldname": "organization_type",
			"label": __("Organization Type"),
			"fieldtype": "Select",
			"options": "\nConference\nUnion\nDivision\nGeneral Conference\nOther"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nPending Approval\nApproved\nSent\nReceived"
		},
		{
			"fieldname": "payment_mode",
			"label": __("Payment Mode"),
			"fieldtype": "Select",
			"options": "\nBank Transfer\nCheque\nCash\nOther"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "status") {
			if (value == "Sent") {
				value = `<span class="indicator green">${value}</span>`;
			} else if (value == "Pending Approval") {
				value = `<span class="indicator orange">${value}</span>`;
			} else if (value == "Draft") {
				value = `<span class="indicator red">${value}</span>`;
			} else if (value == "Approved") {
				value = `<span class="indicator blue">${value}</span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom button to show pending balance
		report.page.add_inner_button(__("Show Pending Balance"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "'stewardpro.stewardpro.report.remittance_report.remittance_report.get_pending_balance",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						frappe.msgprint({
							title: __("Pending Remittance Balance"),
							message: `
								<table class="table table-bordered">
									<tr>
										<td><strong>Total to Remit:</strong></td>
										<td>${format_currency(data.total_to_remit)}</td>
									</tr>
									<tr>
										<td><strong>Total Remitted:</strong></td>
										<td>${format_currency(data.total_remitted)}</td>
									</tr>
									<tr class="${data.pending_balance > 0 ? 'text-danger' : 'text-success'}">
										<td><strong>Pending Balance:</strong></td>
										<td><strong>${format_currency(data.pending_balance)}</strong></td>
									</tr>
								</table>
							`,
							wide: true
						});
					}
				}
			});
		});
	}
};
