// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Annual Conference Report"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": get_year_options(),
			"default": new Date().getFullYear().toString(),
			"reqd": 1
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Format category headers
		if (column.fieldname == "category" && data && data.category.includes("<b>")) {
			return value;
		}
		
		// Format change amounts and percentages
		if (column.fieldname == "change_amount" && data) {
			if (data.change_amount > 0) {
				value = `<span class="text-success">+${value}</span>`;
			} else if (data.change_amount < 0) {
				value = `<span class="text-danger">${value}</span>`;
			}
		}
		
		if (column.fieldname == "change_percentage" && data) {
			if (data.change_percentage > 0) {
				value = `<span class="text-success">+${value}%</span>`;
			} else if (data.change_percentage < 0) {
				value = `<span class="text-danger">${value}%</span>`;
			}
		}
		
		// Highlight net balance
		if (column.fieldname == "amount" && data && data.category.includes("NET BALANCE")) {
			if (data.amount > 0) {
				value = `<span class="text-success"><strong>${value}</strong></span>`;
			} else if (data.amount < 0) {
				value = `<span class="text-danger"><strong>${value}</strong></span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom button to export for conference
		report.page.add_inner_button(__("Export for Conference"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "frappe.desk.query_report.export_query",
				args: {
					report_name: "Annual Conference Report",
					file_format_type: "Excel",
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						window.open(frappe.urllib.get_full_url(r.message));
					}
				}
			});
		});
		
		// Add button to compare with previous year
		report.page.add_inner_button(__("Year Comparison"), function() {
			let current_year = report.get_values().year;
			let previous_year = parseInt(current_year) - 1;
			
			frappe.msgprint({
				title: __("Year-over-Year Comparison"),
				message: `
					<p>This report shows comparison between ${current_year} and ${previous_year}.</p>
					<p><strong>Key Metrics to Review:</strong></p>
					<ul>
						<li>Total Income Growth/Decline</li>
						<li>Tithe Faithfulness Trends</li>
						<li>Special Offerings Performance</li>
						<li>Expense Management Efficiency</li>
						<li>Net Balance Health</li>
					</ul>
					<p><em>Green values indicate positive growth, red values indicate decline.</em></p>
				`,
				wide: true
			});
		});
		
		// Add button to view detailed breakdown
		report.page.add_inner_button(__("Detailed Breakdown"), function() {
			let year = report.get_values().year;
			
			// Open multiple related reports in new tabs
			frappe.set_route("query-report", "Tithes and Offerings Report", {
				from_date: `${year}-01-01`,
				to_date: `${year}-12-31`
			});
		});
	}
};

function get_year_options() {
	let current_year = new Date().getFullYear();
	let years = [];
	
	for (let i = current_year; i >= current_year - 10; i--) {
		years.push(i.toString());
	}
	
	return years.join('\n');
}
