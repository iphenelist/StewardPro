// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Pending Remittance Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "amount_pending") {
			if (data && data.amount_pending > 0) {
				value = `<span class="text-danger"><strong>${value}</strong></span>`;
			} else {
				value = `<span class="text-success">${value}</span>`;
			}
		}
		
		if (column.fieldname == "pending_percentage") {
			if (data && data.pending_percentage > 50) {
				value = `<span class="text-danger"><strong>${value}%</strong></span>`;
			} else if (data && data.pending_percentage > 20) {
				value = `<span class="text-warning">${value}%</span>`;
			} else {
				value = `<span class="text-success">${value}%</span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom button to show overall summary
		report.page.add_inner_button(__("Overall Summary"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "stewardpro.church_management.report.pending_remittance_report.pending_remittance_report.get_overall_summary",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						
						frappe.msgprint({
							title: __("Overall Remittance Summary"),
							message: `
								<table class="table table-bordered">
									<tr>
										<td><strong>Total Tithes Collected:</strong></td>
										<td>${format_currency(data.total_tithes)}</td>
									</tr>
									<tr>
										<td><strong>Total Offerings to Field:</strong></td>
										<td>${format_currency(data.total_offerings_to_field)}</td>
									</tr>
									<tr>
										<td><strong>Total Special Offerings:</strong></td>
										<td>${format_currency(data.total_special_offerings)}</td>
									</tr>
									<tr class="table-info">
										<td><strong>Total to Remit:</strong></td>
										<td><strong>${format_currency(data.total_to_remit)}</strong></td>
									</tr>
									<tr>
										<td><strong>Total Remitted:</strong></td>
										<td>${format_currency(data.total_remitted)}</td>
									</tr>
									<tr class="${data.total_pending > 0 ? 'table-danger' : 'table-success'}">
										<td><strong>Total Pending:</strong></td>
										<td><strong>${format_currency(data.total_pending)}</strong></td>
									</tr>
									<tr>
										<td><strong>Pending Percentage:</strong></td>
										<td class="${data.pending_percentage > 50 ? 'text-danger' : data.pending_percentage > 20 ? 'text-warning' : 'text-success'}">
											<strong>${data.pending_percentage.toFixed(2)}%</strong>
										</td>
									</tr>
								</table>
							`,
							wide: true
						});
					}
				}
			});
		});
		
		// Add button to create remittance for pending amounts
		report.page.add_inner_button(__("Create Remittance"), function() {
			frappe.set_route("remittance-manager");
		});
	}
};
