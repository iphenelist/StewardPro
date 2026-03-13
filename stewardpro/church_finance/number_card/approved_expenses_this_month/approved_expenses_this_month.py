import frappe
from frappe.utils import flt, get_first_day, get_last_day, today


@frappe.whitelist()
def get():
	start_date = get_first_day(today())
	end_date = get_last_day(today())
	value = frappe.db.sql(
		"""
		SELECT SUM(amount)
		FROM `tabChurch Expense`
		WHERE docstatus = 1
		  AND expense_date BETWEEN %s AND %s
		""",
		(start_date, end_date),
	)[0][0] or 0
	return {
		"value": flt(value),
		"fieldtype": "Currency",
		"route": ["query-report", "Church Expense Register"],
		"route_options": {
			"from_date": start_date,
			"to_date": end_date,
			"approval_status": "Approved",
		},
	}
