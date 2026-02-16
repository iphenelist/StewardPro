// Copyright (c) 2026, StewardPro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Member", {
	refresh: function(frm) {
		// Auto-set full name display
	},
	first_name: function(frm) {
		frm.trigger("set_full_name");
	},
	middle_name: function(frm) {
		frm.trigger("set_full_name");
	},
	last_name: function(frm) {
		frm.trigger("set_full_name");
	},
	set_full_name: function(frm) {
		var parts = [frm.doc.first_name, frm.doc.middle_name, frm.doc.last_name];
		var full_name = parts.filter(function(p) { return p; }).join(" ");
		frm.set_value("full_name", full_name);
	}
});
