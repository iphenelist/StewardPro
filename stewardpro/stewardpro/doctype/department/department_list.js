// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.listview_settings['Department'] = {
	add_fields: ["is_active", "department_code", "annual_budget"],
	filters: [["is_active", "=", 1]],
	
	get_indicator: function(doc) {
		if (doc.is_active) {
			return [__("Active"), "green", "is_active,=,1"];
		} else {
			return [__("Inactive"), "red", "is_active,=,0"];
		}
	},
	
	formatters: {
		annual_budget: function(value) {
			if (value) {
				return format_currency(value);
			}
			return "";
		}
	},
	
	onload: function(listview) {
		// Add custom buttons to list view
		listview.page.add_menu_item(__("Department Tree"), function() {
			frappe.set_route("Tree", "Department");
		});
		
		listview.page.add_menu_item(__("Budget Summary"), function() {
			show_budget_summary();
		});
	}
};

function show_budget_summary() {
	frappe.call({
		method: "'stewardpro.stewardpro.doctype.department.department.get_active_departments",
		callback: function(r) {
			if (r.message) {
				let departments = r.message;
				let total_budget = 0;
				
				let html = `
					<div class="table-responsive">
						<table class="table table-bordered">
							<thead>
								<tr>
									<th>Department</th>
									<th>Code</th>
									<th>Annual Budget</th>
								</tr>
							</thead>
							<tbody>
				`;
				
				departments.forEach(function(dept) {
					// Get budget for each department
					frappe.call({
						method: "frappe.client.get_value",
						args: {
							doctype: "Department",
							filters: {"name": dept.name},
							fieldname: "annual_budget"
						},
						async: false,
						callback: function(budget_r) {
							let budget = budget_r.message ? budget_r.message.annual_budget || 0 : 0;
							total_budget += budget;
							
							html += `
								<tr>
									<td><a href="/app/department/${dept.name}">${dept.department_name}</a></td>
									<td>${dept.department_code}</td>
									<td>${format_currency(budget)}</td>
								</tr>
							`;
						}
					});
				});
				
				html += `
							</tbody>
							<tfoot>
								<tr style="font-weight: bold;">
									<td colspan="2">Total Budget</td>
									<td>${format_currency(total_budget)}</td>
								</tr>
							</tfoot>
						</table>
					</div>
				`;
				
				frappe.msgprint({
					title: __('Department Budget Summary'),
					message: html,
					wide: true
				});
			}
		}
	});
}
