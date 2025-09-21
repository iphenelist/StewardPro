// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department Budget Item', {
	refresh: function(frm) {
		// Set item filter based on parent department
		set_item_filter(frm);
	},
	
	item: function(frm) {
		// Auto-populate category from item
		if (frm.doc.item) {
			frappe.db.get_value('Item', frm.doc.item, ['category', 'standard_cost', 'description', 'unit_of_measure'], function(r) {
				if (r) {
					// Always update category from selected item
					if (r.category) {
						frm.set_value('category', r.category);
					}
					// Update budgeted amount if not already set
					if (r.standard_cost && !frm.doc.budgeted_amount) {
						frm.set_value('budgeted_amount', r.standard_cost);
					}
					// Update description if not already set
					if (r.description && !frm.doc.description) {
						frm.set_value('description', r.description);
					}
				}
			});
		} else {
			// Clear category when item is cleared
			frm.set_value('category', '');
		}
	}
});

function set_item_filter(frm) {
	// Get parent department and filter items accordingly
	if (frm.doc.parent && frm.doc.parenttype === 'Department Budget') {
		frappe.db.get_value('Department Budget', frm.doc.parent, 'department', function(r) {
			if (r && r.department) {
				frm.set_query('item', function() {
					return {
						filters: {
							'department': r.department,
							'is_active': 1
						}
					};
				});
			}
		});
	}
}
