// Copyright (c) 2026, StewardPro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Account", {
	refresh: function(frm) {
		frm.trigger("set_root_readonly");
	},
	set_root_readonly: function(frm) {
		if (!frm.doc.parent_account && !frm.doc.__islocal) {
			frm.set_read_only();
			frm.set_intro(__("This is a root account and cannot be edited."));
		}
	}
});

frappe.treeview_settings["Church Account"] = {
	breadcrumb: "Church Finance",
	get_tree_root: false,
	root_label: "Church Accounts",
	filters: [
		{
			fieldname: "account_type",
			fieldtype: "Select",
			options: ["", "Income", "Expense", "Asset", "Liability"],
			label: __("Account Type")
		}
	],
	fields: [
		{
			fieldtype: "Data",
			fieldname: "account_name",
			label: __("Account Name"),
			reqd: true
		},
		{
			fieldtype: "Select",
			fieldname: "account_type",
			label: __("Account Type"),
			options: "\nIncome\nExpense\nAsset\nLiability",
			reqd: true
		}
	]
};
