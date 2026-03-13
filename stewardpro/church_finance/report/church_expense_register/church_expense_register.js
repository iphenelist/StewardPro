frappe.query_reports["Church Expense Register"] = {
	filters: [
		{
			fieldname: "from_date",
			fieldtype: "Date",
			label: __("From Date"),
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			fieldtype: "Date",
			label: __("To Date"),
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "department",
			fieldtype: "Link",
			label: __("Department"),
			options: "Church Department",
		},
		{
			fieldname: "account",
			fieldtype: "Link",
			label: __("Expense Account"),
			options: "Church Account",
		},
		{
			fieldname: "paid_from",
			fieldtype: "Link",
			label: __("Paid From Account"),
			options: "Church Account",
		},
		{
			fieldname: "approval_status",
			fieldtype: "Select",
			label: __("Approval Status"),
			options: "\nDraft\nPending Approval\nApproved\nRejected",
		},
		{
			fieldname: "payment_method",
			fieldtype: "Select",
			label: __("Payment Method"),
			options: "\nCash\nMobile Money\nBank Transfer\nCheque",
		},
	],
};
