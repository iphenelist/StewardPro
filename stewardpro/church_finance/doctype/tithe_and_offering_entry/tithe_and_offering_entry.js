// Copyright (c) 2026, StewardPro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tithe and Offering Entry", {
	refresh: function(frm) {
	},

	tithe: function(frm) {
		frm.trigger("calculate_totals");
	},

	offering: function(frm) {
		frm.trigger("calculate_totals");
	},

	camp_meeting: function(frm) {
		frm.trigger("calculate_totals");
	},

	church_building_fund: function(frm) {
		frm.trigger("calculate_totals");
	},

	calculate_totals: function(frm) {
		let tithe = flt(frm.doc.tithe);
		let offering = flt(frm.doc.offering);
		let camp_meeting = flt(frm.doc.camp_meeting);
		let building_fund = flt(frm.doc.church_building_fund);

		// Offering split: 42% local, 56% conference
		let offering_local = flt(offering * 42 / 100, 2);
		let offering_conference = flt(offering * 56 / 100, 2);

		frm.set_value("offering_local_share", 42);
		frm.set_value("offering_conference_share", 56);
		frm.set_value("offering_local_amount", offering_local);
		frm.set_value("offering_conference_amount", offering_conference);

		frm.set_value("total_tithe_and_offerings", tithe + offering + camp_meeting + building_fund);
		frm.set_value("total_for_conference", tithe + offering_conference + camp_meeting);
		frm.set_value("total_for_local_church", offering_local + building_fund);
		frm.set_value("grand_total", tithe + offering_conference + camp_meeting + offering_local + building_fund);
	}
});
