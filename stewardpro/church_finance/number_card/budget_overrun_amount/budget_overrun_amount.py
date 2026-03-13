import frappe
from frappe.utils import flt

from stewardpro.church_finance.doctype.church_budget.church_budget import refresh_expense_actuals


@frappe.whitelist()
def get():
	refresh_expense_actuals()
	rows = frappe.db.sql(
		"""
		SELECT ABS(variance) AS overrun
		FROM `tabBudget Line Item`
		WHERE parenttype = 'Church Budget'
		  AND parentfield = 'expense_items'
		  AND variance < 0
		""",
		as_dict=True,
	)
	value = sum(flt(row.overrun) for row in rows)
	return {
		"value": value,
		"fieldtype": "Currency",
		"route": ["query-report", "Expense Budget Variance"],
		"route_options": {"show_only_over_budget": 1},
	}
