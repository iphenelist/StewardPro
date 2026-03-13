import frappe


@frappe.whitelist()
def get():
	value = frappe.db.count(
		"Church Expense",
		{"docstatus": 0, "approval_status": "Pending Approval"},
	)
	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Church Expense", "List"],
		"route_options": {"approval_status": "Pending Approval"},
	}
