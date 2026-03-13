// Copyright (c) 2026, StewardPro and contributors
// For license information, please see license.txt

frappe.ui.form.on("Church Expense", {
	setup(frm) {
		set_account_queries(frm);
	},

	refresh(frm) {
		set_account_queries(frm);
		set_form_context(frm);
	},

	department(frm) {
		set_account_queries(frm);
		clear_invalid_selection(frm, "account");
		clear_invalid_selection(frm, "paid_from");
	},

	account(frm) {
		if (!frm.doc.account || frm.doc.department) {
			return;
		}

		frappe.db.get_value("Church Account", frm.doc.account, "department").then(({ message }) => {
			if (message?.department) {
				frm.set_value("department", message.department);
			}
		});
	},
});

function set_account_queries(frm) {
	frm.set_query("account", () => ({
		query: "stewardpro.church_finance.doctype.church_expense.church_expense.get_expense_accounts",
		filters: {
			department: frm.doc.department || "",
		},
	}));

	frm.set_query("paid_from", () => ({
		query: "stewardpro.church_finance.doctype.church_expense.church_expense.get_paid_from_accounts",
		filters: {
			department: frm.doc.department || "",
		},
	}));
}

function set_form_context(frm) {
	if (frm.doc.docstatus === 1) {
		frm.dashboard.set_headline_alert(__("This expense has been approved and posted to the selected accounts."));
		return;
	}

	const status = frm.doc.approval_status || "Draft";
	const headline = {
		"Draft": __("Complete the details, then submit the expense for approval."),
		"Pending Approval": __("This expense is waiting for approval before it can affect account balances."),
		"Rejected": __("This expense was rejected. Update the details and resubmit when ready."),
	}[status];

	if (headline) {
		frm.dashboard.set_headline_alert(headline);
	}
}

function clear_invalid_selection(frm, fieldname) {
	const value = frm.doc[fieldname];
	if (!value) {
		return;
	}

	frappe.db
		.get_value("Church Account", value, ["department", "account_type"])
		.then(({ message }) => {
			if (!message) {
				return;
			}

			const wrong_type =
				(fieldname === "account" && message.account_type !== "Expense") ||
				(fieldname === "paid_from" && message.account_type !== "Asset");
			const wrong_department =
				frm.doc.department &&
				message.department &&
				message.department !== frm.doc.department;

			if (wrong_type || wrong_department) {
				frm.set_value(fieldname, "");
			}
		});
}
