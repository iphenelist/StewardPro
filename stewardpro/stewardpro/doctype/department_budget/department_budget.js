// Copyright (c) 2025, Innocent P Metumba and contributors
// For license information, please see license.txt

frappe.ui.form.on("Department Budget", {
	refresh: function(frm) {
		// Set item filter for budget items table
		set_item_filter_for_budget_items(frm);
	},

	department: function(frm) {
		// Update item filter when department changes
		set_item_filter_for_budget_items(frm);

		// Clear existing budget items when department changes
		frm.clear_table('budget_items');
		frm.refresh_field('budget_items');
	},
});

frappe.ui.form.on("Department Budget Item", {
	item: function(frm, cdt, cdn) {
		// Auto-populate category and cost when item is selected
		let row = locals[cdt][cdn];
		if (row.item) {
			frappe.db.get_value('Item', row.item, ['category', 'standard_cost', 'description'], function(r) {
				if (r) {
					if (r.category) {
						frappe.model.set_value(cdt, cdn, 'category', r.category);
					}
					if (r.standard_cost && !row.unit_price) {
						frappe.model.set_value(cdt, cdn, 'unit_price', r.standard_cost);
					}
					if (r.description && !row.description) {
						frappe.model.set_value(cdt, cdn, 'description', r.description);
					}
					// Calculate budgeted amount
					calculate_budget_item_amount(frm, cdt, cdn);
				}
			});
		}
	},

	quantity: function(frm, cdt, cdn) {
		calculate_budget_item_amount(frm, cdt, cdn);
	},

	unit_price: function(frm, cdt, cdn) {
		calculate_budget_item_amount(frm, cdt, cdn);
	},

	budgeted_amount: function(frm) {
		calculate_total_budget_amount(frm);
	},

	budget_items_remove: function(frm) {
		calculate_total_budget_amount(frm);
	}
});

function calculate_budget_item_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.quantity && row.unit_price) {
		let budgeted_amount = row.quantity * row.unit_price;
		frappe.model.set_value(cdt, cdn, 'budgeted_amount', budgeted_amount);

		// Trigger total calculation in parent
		calculate_total_budget_amount(frm);
	}
}

function calculate_total_budget_amount(frm) {
	let total = 0;
	frm.doc.budget_items.forEach(function(row) {
		if (row.budgeted_amount) {
			total += row.budgeted_amount;
		}
	});
	frm.set_value('total_budget_amount', total);
}

function set_item_filter_for_budget_items(frm) {
	if (frm.doc.department) {
		frm.set_query('item', 'budget_items', function() {
			return {
				filters: {
					'department': frm.doc.department,
					'is_active': 1
				}
			};
		});
	}
}
