// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Departmental Budget Report"] = {
	"filters": [
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year")
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Select",
			"options": "\nSabbath School\nYouth Ministry\nChildren's Ministry\nMusic Ministry\nCommunity Services\nWomen's Ministry\nMen's Ministry\nHealth Ministry\nEducation Ministry\nEvangelism\nStewardship\nFamily Life\nCommunication\nMaintenance\nOther"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nSubmitted\nApproved\nActive\nClosed"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "utilization_percentage") {
			if (value > 100) {
				value = `<span class="text-danger"><strong>${value}%</strong></span>`;
			} else if (value > 80) {
				value = `<span class="text-warning">${value}%</span>`;
			} else {
				value = `<span class="text-success">${value}%</span>`;
			}
		}
		
		if (column.fieldname == "status") {
			if (value == "Active") {
				value = `<span class="indicator green">${value}</span>`;
			} else if (value == "Approved") {
				value = `<span class="indicator blue">${value}</span>`;
			} else if (value == "Draft") {
				value = `<span class="indicator orange">${value}</span>`;
			} else if (value == "Closed") {
				value = `<span class="indicator red">${value}</span>`;
			}
		}
		
		if (column.fieldname == "remaining_amount" && data) {
			if (data.remaining_amount < 0) {
				value = `<span class="text-danger">${value}</span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom button to show budget summary
		report.page.add_inner_button(__("Budget Summary"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "stewardpro.church_management.report.departmental_budget_report.departmental_budget_report.get_summary_data",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						let overall_utilization = data.total_allocated > 0 ? 
							((data.total_spent / data.total_allocated) * 100).toFixed(2) : 0;
						
						frappe.msgprint({
							title: __("Budget Summary"),
							message: `
								<table class="table table-bordered">
									<tr>
										<td><strong>Total Budgets:</strong></td>
										<td>${data.total_budgets || 0}</td>
									</tr>
									<tr>
										<td><strong>Total Allocated:</strong></td>
										<td>${format_currency(data.total_allocated || 0)}</td>
									</tr>
									<tr>
										<td><strong>Total Spent:</strong></td>
										<td>${format_currency(data.total_spent || 0)}</td>
									</tr>
									<tr>
										<td><strong>Total Remaining:</strong></td>
										<td class="${(data.total_remaining || 0) < 0 ? 'text-danger' : 'text-success'}">
											${format_currency(data.total_remaining || 0)}
										</td>
									</tr>
									<tr>
										<td><strong>Overall Utilization:</strong></td>
										<td class="${overall_utilization > 100 ? 'text-danger' : overall_utilization > 80 ? 'text-warning' : 'text-success'}">
											<strong>${overall_utilization}%</strong>
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
		
		// Add button to create new budget
		report.page.add_inner_button(__("New Budget"), function() {
			frappe.new_doc("Department Budget");
		});
	}
};
