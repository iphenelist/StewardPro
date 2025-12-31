// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.doc.__islocal) {			
			frm.add_custom_button(__('Budget Report'), function() {
				frappe.route_options = {
					"department": frm.doc.name
				};
				frappe.set_route("query-report", "Departmental Budget Report");
			});
		}
		
		// Set default budget year
		if (frm.doc.__islocal && !frm.doc.budget_year) {
			frm.set_value('budget_year', new Date().getFullYear());
		}
		frm.set_query('department_head', () => {
			return {
				filters: {
					role: 'Department Head'
				}
			}
		})
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
