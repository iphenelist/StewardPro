// Copyright (c) 2026, StewardPro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tithe and Offering Entry", {
	refresh: function(frm) {
	}
});

frappe.ui.form.on("Tithe Offering Item", {
	amount: function(frm) {
		frm.trigger("calculate_totals");
	},
	items_remove: function(frm) {
		frm.trigger("calculate_totals");
	}
});
