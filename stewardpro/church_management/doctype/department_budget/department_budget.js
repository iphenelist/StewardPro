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
					if (r.standard_cost && !row.budgeted_amount) {
						frappe.model.set_value(cdt, cdn, 'budgeted_amount', r.standard_cost);
					}
					if (r.description && !row.description) {
						frappe.model.set_value(cdt, cdn, 'description', r.description);
					}
				}
			});
		}
	}
});

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
