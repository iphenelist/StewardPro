// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Camp Meeting Contributions Report"] = {
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
			"fieldname": "member",
			"label": __("Member"),
			"fieldtype": "Link",
			"options": "Member"
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
		// Add custom button to show member summary
		report.page.add_inner_button(__("Member Summary"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "stewardpro.stewardpro.report.camp_meeting_contributions_report.camp_meeting_contributions_report.get_member_summary",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						let html = "<table class='table table-striped'>";
						html += "<thead><tr><th>Member</th><th>Contributions</th><th>Total Amount</th></tr></thead><tbody>";
						
						data.forEach(function(row) {
							html += `<tr>
								<td>${row.member_name || 'Anonymous'}</td>
								<td>${row.contribution_count}</td>
								<td>${format_currency(row.total_contribution)}</td>
							</tr>`;
						});
						
						html += "</tbody></table>";
						
						frappe.msgprint({
							title: __("Camp Meeting Contributions by Member"),
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
