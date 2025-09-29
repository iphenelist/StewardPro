// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('View Budget Items'), function() {
				frappe.set_route('List', 'Department Budget Item', {
					'item': frm.doc.name
				});
			});

			frm.add_custom_button(__('View Expenses'), function() {
				frappe.set_route('List', 'Department Expense', {
					'item': frm.doc.name
				});
			});

			// Add button to show item usage summary
			frm.add_custom_button(__('Usage Summary'), function() {
				show_item_usage_summary(frm);
			});
		}
		
		// Set indicator based on active status
		if (frm.doc.is_active) {
			frm.dashboard.set_headline_alert(
				'<div class="row">' +
				'<div class="col-xs-12">' +
				'<span class="indicator green">Active</span>' +
				'</div>' +
				'</div>'
			);
		} else {
			frm.dashboard.set_headline_alert(
				'<div class="row">' +
				'<div class="col-xs-12">' +
				'<span class="indicator red">Inactive</span>' +
				'</div>' +
				'</div>'
			);
		}
	},
	
	department: function(frm) {
		// Clear category when department changes to ensure proper filtering
		if (frm.doc.department) {
			// You can add department-specific category filtering here if needed
		}
	},
	
	category: function(frm) {
		// Update standard cost based on category if needed
		if (frm.doc.category && !frm.doc.standard_cost) {
			// Set default costs based on category
			let default_costs = {
				'Equipment': 1000,
				'Supplies': 100,
				'Events': 500,
				'Training': 300,
				'Travel': 200,
				'Utilities': 150,
				'Maintenance': 250,
				'Salaries': 2000,
				'Rent': 1500,
				'Insurance': 400,
				'Other': 100
			};
			
			if (default_costs[frm.doc.category]) {
				frm.set_value('standard_cost', default_costs[frm.doc.category]);
			}
		}
	},
	
	item_name: function(frm) {
		// Auto-format item name
		if (frm.doc.item_name) {
			frm.set_value('item_name', frm.doc.item_name.trim());
		}
	},

	department: function(frm) {
		// When department changes, validate that category is appropriate
		if (frm.doc.department && frm.doc.category) {
			// You can add department-specific category validation here if needed
		}
	}
});

function show_item_usage_summary(frm) {
	// Show where this item is being used
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Department Budget Item',
			filters: {
				'item': frm.doc.name
			},
			fields: ['parent', 'budgeted_amount', 'spent_amount']
		},
		callback: function(r) {
			let budget_usage = r.message || [];

			frappe.call({
				method: 'frappe.client.get_list',
				args: {
					doctype: 'Department Expense',
					filters: {
						'item': frm.doc.name,
						'docstatus': 1
					},
					fields: ['name', 'amount', 'expense_date']
				},
				callback: function(r2) {
					let expense_usage = r2.message || [];

					let html = '<div class="row">';
					html += '<div class="col-md-6">';
					html += '<h5>Budget Allocations</h5>';
					if (budget_usage.length > 0) {
						html += '<ul>';
						budget_usage.forEach(function(item) {
							html += '<li>' + item.parent + ' - Budgeted: ' + format_currency(item.budgeted_amount);
							if (item.spent_amount) {
								html += ', Spent: ' + format_currency(item.spent_amount);
							}
							html += '</li>';
						});
						html += '</ul>';
					} else {
						html += '<p>No budget allocations found.</p>';
					}
					html += '</div>';

					html += '<div class="col-md-6">';
					html += '<h5>Actual Expenses</h5>';
					if (expense_usage.length > 0) {
						html += '<ul>';
						expense_usage.forEach(function(item) {
							html += '<li>' + item.name + ' - ' + format_currency(item.amount) + ' (' + item.expense_date + ')</li>';
						});
						html += '</ul>';
					} else {
						html += '<p>No expenses found.</p>';
					}
					html += '</div>';
					html += '</div>';

					frappe.msgprint({
						title: __('Item Usage Summary: ') + frm.doc.item_name,
						message: html,
						wide: true
					});
				}
			});
		}
	});
}
