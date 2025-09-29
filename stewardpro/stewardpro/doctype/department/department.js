// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('View Expenses'), function() {
				frappe.route_options = {
					"department": frm.doc.name
				};
				frappe.set_route("List", "Expense");
			});
			
			frm.add_custom_button(__('Budget Report'), function() {
				frappe.route_options = {
					"department": frm.doc.name
				};
				frappe.set_route("query-report", "Departmental Budget Report");
			});
			
			frm.add_custom_button(__('Budget Utilization'), function() {
				show_budget_utilization(frm);
			});
		}
		
		// Set default budget year
		if (frm.doc.__islocal && !frm.doc.budget_year) {
			frm.set_value('budget_year', new Date().getFullYear());
		}
	},
	
	department_code: function(frm) {
		// Convert department code to uppercase
		if (frm.doc.department_code) {
			frm.set_value('department_code', frm.doc.department_code.toUpperCase());
		}
	},
	
	parent_department: function(frm) {
		// Validate that department is not its own parent
		if (frm.doc.parent_department === frm.doc.name) {
			frappe.msgprint(__('Department cannot be its own parent'));
			frm.set_value('parent_department', '');
		}
	}
});

function show_budget_utilization(frm) {
	frappe.call({
		method: 'get_budget_utilization',
		doc: frm.doc,
		args: {
			year: frm.doc.budget_year || new Date().getFullYear()
		},
		callback: function(r) {
			if (r.message) {
				let data = r.message;
				let utilization_color = 'green';
				
				if (data.utilization_percentage > 90) {
					utilization_color = 'red';
				} else if (data.utilization_percentage > 75) {
					utilization_color = 'orange';
				}
				
				let html = `
					<div class="row">
						<div class="col-md-6">
							<h5>Budget Utilization for ${frm.doc.budget_year || new Date().getFullYear()}</h5>
							<table class="table table-bordered">
								<tr>
									<td><strong>Annual Budget</strong></td>
									<td>${format_currency(data.budget)}</td>
								</tr>
								<tr>
									<td><strong>Total Expenses</strong></td>
									<td>${format_currency(data.expenses)}</td>
								</tr>
								<tr>
									<td><strong>Remaining Budget</strong></td>
									<td style="color: ${data.remaining >= 0 ? 'green' : 'red'}">
										${format_currency(data.remaining)}
									</td>
								</tr>
								<tr>
									<td><strong>Utilization</strong></td>
									<td style="color: ${utilization_color}">
										${data.utilization_percentage.toFixed(1)}%
									</td>
								</tr>
							</table>
						</div>
						<div class="col-md-6">
							<div class="progress" style="height: 30px; margin-top: 20px;">
								<div class="progress-bar" role="progressbar" 
									style="width: ${Math.min(data.utilization_percentage, 100)}%; background-color: ${utilization_color};"
									aria-valuenow="${data.utilization_percentage}" 
									aria-valuemin="0" aria-valuemax="100">
									${data.utilization_percentage.toFixed(1)}%
								</div>
							</div>
						</div>
					</div>
				`;
				
				frappe.msgprint({
					title: __('Budget Utilization'),
					message: html,
					wide: true
				});
			}
		}
	});
}

// Department Tree View
frappe.treeview_settings["Department"] = {
	get_tree_nodes: "'stewardpro.stewardpro.doctype.department.department.get_department_tree",
	filters: [
		{
			fieldname: "is_active",
			fieldtype: "Check",
			label: __("Is Active"),
			default: 1
		}
	],
	breadcrumb: "Church Management",
	get_tree_root: false,
	show_expand_all: true,
	onload: function(treeview) {
		treeview.make_tree();
	},
	toolbar: [
		{
			label: __("Add Department"),
			condition: function(node) {
				return frappe.boot.user.can_create.indexOf("Department") !== -1;
			},
			click: function(node) {
				frappe.new_doc("Department", {
					parent_department: node.data.value !== "All Departments" ? node.data.value : ""
				});
			}
		}
	],
	menu_items: [
		{
			label: __("New Department"),
			action: function() {
				frappe.new_doc("Department");
			},
			condition: 'frappe.boot.user.can_create.indexOf("Department") !== -1'
		}
	]
};
