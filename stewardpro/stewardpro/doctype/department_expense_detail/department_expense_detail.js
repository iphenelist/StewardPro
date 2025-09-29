// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department Expense Detail', {
	item: function(frm, cdt, cdn) {
		// Auto-populate category, description, and unit price from item
		let row = locals[cdt][cdn];
		if (row.item) {
			frappe.db.get_value('Item', row.item, ['category', 'description', 'standard_cost'], function(r) {
				if (r) {
					if (r.category) {
						frappe.model.set_value(cdt, cdn, 'expense_category', r.category);
					}
					if (r.description && !row.expense_description) {
						frappe.model.set_value(cdt, cdn, 'expense_description', r.description);
					}
					if (r.standard_cost && !row.unit_price) {
						frappe.model.set_value(cdt, cdn, 'unit_price', r.standard_cost);
					}
				}
			});
		}
	},
	
	quantity: function(frm, cdt, cdn) {
		// Calculate amount when quantity changes
		calculate_amount(frm, cdt, cdn);
	},
	
	unit_price: function(frm, cdt, cdn) {
		// Calculate amount when unit price changes
		calculate_amount(frm, cdt, cdn);
	}
});

function calculate_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.quantity && row.unit_price) {
		let amount = row.quantity * row.unit_price;
		frappe.model.set_value(cdt, cdn, 'amount', amount);
		
		// Trigger total calculation in parent
		calculate_total_amount(frm);
	}
}

function calculate_total_amount(frm) {
	let total = 0;
	frm.doc.expense_details.forEach(function(row) {
		if (row.amount) {
			total += row.amount;
		}
	});
	frm.set_value('total_amount', total);
}
