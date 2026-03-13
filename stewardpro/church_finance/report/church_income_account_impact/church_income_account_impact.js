frappe.query_reports["Church Income Account Impact"] = {
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
			fieldname: "destination",
			fieldtype: "Select",
			label: __("Destination"),
			options: "\nLocal Church\nConference",
		},
		{
			fieldname: "member",
			fieldtype: "Link",
			label: __("Member"),
			options: "Church Member",
		},
		{
			fieldname: "payment_method",
			fieldtype: "Select",
			label: __("Payment Method"),
			options: "\nCash\nMobile Money\nBank Transfer\nCheque",
		},
		{
			fieldname: "account",
			fieldtype: "Link",
			label: __("Income Account"),
			options: "Church Account",
			get_query() {
				return {
					filters: {
						account_type: "Income",
					},
				};
			},
		},
		{
			fieldname: "show_zero_accounts",
			fieldtype: "Check",
			label: __("Show Zero Accounts"),
			default: 0,
		},
	],
};
