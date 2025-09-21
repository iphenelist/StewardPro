// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Expense Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "expense_category",
			"label": __("Category"),
			"fieldtype": "Select",
			"options": "\nEquipment\nSupplies\nEvents\nTraining\nTravel\nUtilities\nMaintenance\nSalaries\nRent\nInsurance\nOther"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nPending Approval\nApproved\nPaid\nRejected"
		},
		{
			"fieldname": "payment_mode",
			"label": __("Payment Mode"),
			"fieldtype": "Select",
			"options": "\nCash\nCheque\nBank Transfer\nMpesa\nCredit Card\nOther"
		},
		{
			"fieldname": "budget_reference",
			"label": __("Budget Reference"),
			"fieldtype": "Link",
			"options": "Department Budget"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "status") {
			if (value == "Approved" || value == "Paid") {
				value = `<span class="indicator green">${value}</span>`;
			} else if (value == "Pending Approval") {
				value = `<span class="indicator orange">${value}</span>`;
			} else if (value == "Draft") {
				value = `<span class="indicator blue">${value}</span>`;
			} else if (value == "Rejected") {
				value = `<span class="indicator red">${value}</span>`;
			}
		}
		
		if (column.fieldname == "amount" && data && data.amount > 10000) {
			value = `<span class="text-warning"><strong>${value}</strong></span>`;
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Add custom button to show expense summary
		report.page.add_inner_button(__("Expense Summary"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "stewardpro.church_management.report.expense_report.expense_report.get_expense_summary",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						
						let dept_html = "<h5>By Department</h5><table class='table table-sm'>";
						data.by_department.forEach(function(dept) {
							dept_html += `<tr><td>${dept.department}</td><td>${dept.count} expenses</td><td>${format_currency(dept.total_amount)}</td></tr>`;
						});
						dept_html += "</table>";
						
						let cat_html = "<h5>By Category</h5><table class='table table-sm'>";
						data.by_category.forEach(function(cat) {
							cat_html += `<tr><td>${cat.expense_category}</td><td>${cat.count} expenses</td><td>${format_currency(cat.total_amount)}</td></tr>`;
						});
						cat_html += "</table>";
						
						frappe.msgprint({
							title: __("Expense Summary"),
							message: dept_html + cat_html,
							wide: true
						});
					}
				}
			});
		});
		
		// Add button to create new expense
		report.page.add_inner_button(__("New Expense"), function() {
			frappe.new_doc("Church Expense");
		});
	}
};
