frappe.query_reports["Department Expense Summary"] = {
	filters: [
		{
			fieldname: "from_date",
			fieldtype: "Date",
			label: __("From Date"),
			default: frappe.datetime.year_start(),
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
			fieldname: "only_submitted",
			fieldtype: "Check",
			label: __("Approved Only"),
			default: 1,
		},
	],
};
