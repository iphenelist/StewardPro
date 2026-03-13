frappe.query_reports["Expense Budget Variance"] = {
	filters: [
		{
			fieldname: "budget",
			fieldtype: "Link",
			label: __("Budget"),
			options: "Church Budget",
		},
		{
			fieldname: "budget_year",
			fieldtype: "Int",
			label: __("Budget Year"),
		},
		{
			fieldname: "budget_period",
			fieldtype: "Select",
			label: __("Budget Period"),
			options: "\nAnnual\nQ1\nQ2\nQ3\nQ4",
		},
		{
			fieldname: "department",
			fieldtype: "Link",
			label: __("Department"),
			options: "Church Department",
		},
		{
			fieldname: "show_only_over_budget",
			fieldtype: "Check",
			label: __("Show Only Over Budget"),
			default: 0,
		},
	],
};
