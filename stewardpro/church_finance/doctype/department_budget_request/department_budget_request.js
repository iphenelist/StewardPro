// Copyright (c) 2026, StewardPro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Department Budget Request", {
	refresh: function(frm) {
		if (frm.doc.church_budget) {
			frm.add_custom_button(__("View Church Budget"), function() {
				frappe.set_route("Form", "Church Budget", frm.doc.church_budget);
			});
		}
		set_account_query(frm);
	},

	department: function(frm) {
		set_account_query(frm);
		// Clear existing account values in items when department changes
		(frm.doc.items || []).forEach(function(row) {
			frappe.model.set_value(row.doctype, row.name, "account", "");
		});
		frm.refresh_field("items");
	}
});

function set_account_query(frm) {
	frm.set_query("account", "items", function() {
		let filters = { account_type: "Expense" };
		if (frm.doc.department) {
			filters["department"] = frm.doc.department;
		}
		return { filters: filters };
	});
}

frappe.ui.form.on("Department Budget Item", {
	quantity: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},

	unit_cost: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},

	amount: function(frm) {
		calculate_total(frm);
	},

	items_remove: function(frm) {
		calculate_total(frm);
	}
});

function calculate_item_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.quantity && row.unit_cost) {
		frappe.model.set_value(cdt, cdn, "amount", flt(row.quantity) * flt(row.unit_cost));
	}
	calculate_total(frm);
}

function calculate_total(frm) {
	let total = 0;
	(frm.doc.items || []).forEach(function(item) {
		total += flt(item.amount);
	});
	frm.set_value("total_requested_amount", total);
}
