// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Church Building Fund Report"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": get_year_options(),
			"default": new Date().getFullYear().toString()
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "contributor",
			"label": __("Contributor"),
			"fieldtype": "Link",
			"options": "Church Member"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "member_name" && data && data.member_name == "Anonymous") {
			value = `<span class="text-muted">${value}</span>`;
		}
		
		if (column.fieldname == "running_total") {
			value = `<strong>${value}</strong>`;
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom button to show contributor summary
		report.page.add_inner_button(__("Contributor Summary"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "stewardpro.church_management.report.church_building_fund_report.church_building_fund_report.get_contributor_summary",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						let html = "<table class='table table-striped'>";
						html += "<thead><tr><th>Contributor</th><th>Contributions</th><th>Total Amount</th></tr></thead><tbody>";
						
						data.forEach(function(row) {
							html += `<tr>
								<td>${row.member_name || 'Anonymous'}</td>
								<td>${row.contribution_count}</td>
								<td>${format_currency(row.total_contribution)}</td>
							</tr>`;
						});
						
						html += "</tbody></table>";
						
						frappe.msgprint({
							title: __("Building Fund Contributors"),
							message: html,
							wide: true
						});
					}
				}
			});
		});
		
		// Add custom button to show monthly summary
		report.page.add_inner_button(__("Monthly Summary"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "stewardpro.church_management.report.church_building_fund_report.church_building_fund_report.get_monthly_summary",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						let html = "<table class='table table-striped'>";
						html += "<thead><tr><th>Month</th><th>Contributions</th><th>Total Amount</th></tr></thead><tbody>";
						
						data.forEach(function(row) {
							html += `<tr>
								<td>${row.month_name} ${row.year}</td>
								<td>${row.contribution_count}</td>
								<td>${format_currency(row.total_contribution)}</td>
							</tr>`;
						});
						
						html += "</tbody></table>";
						
						frappe.msgprint({
							title: __("Monthly Building Fund Summary"),
							message: html,
							wide: true
						});
					}
				}
			});
		});
	}
};

function get_year_options() {
	let current_year = new Date().getFullYear();
	let years = [];
	
	for (let i = current_year; i >= current_year - 5; i--) {
		years.push(i.toString());
	}
	
	return years.join('\n');
}
