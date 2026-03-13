# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ChurchBudget(Document):
	def before_save(self):
		self.calculate_totals()

	def calculate_totals(self):
		self.total_budgeted_income = sum(flt(item.budgeted_amount) for item in self.income_items)
		self.total_budgeted_expense = sum(flt(item.budgeted_amount) for item in self.expense_items)
		self.surplus_deficit = flt(self.total_budgeted_income) - flt(self.total_budgeted_expense)


def refresh_expense_actuals(account_names=None, expense_date=None):
	"""Update actual and variance figures for expense budget lines."""
	budget_filters = {"docstatus": ("<", 2)}
	if expense_date:
		budget_filters["start_date"] = ("<=", expense_date)
		budget_filters["end_date"] = (">=", expense_date)

	budgets = frappe.get_all(
		"Church Budget",
		filters=budget_filters,
		fields=["name", "start_date", "end_date"],
	)
	account_name_set = {account for account in (account_names or []) if account}

	for budget in budgets:
		rows = frappe.get_all(
			"Budget Line Item",
			filters={
				"parent": budget.name,
				"parenttype": "Church Budget",
				"parentfield": "expense_items",
			},
			fields=["name", "account", "budgeted_amount"],
		)

		for row in rows:
			if account_name_set and row.account not in account_name_set:
				continue

			actual_amount = frappe.db.sql(
				"""
				SELECT SUM(amount)
				FROM `tabChurch Expense`
				WHERE docstatus = 1
				  AND account = %s
				  AND expense_date BETWEEN %s AND %s
				""",
				(row.account, budget.start_date, budget.end_date),
			)[0][0] or 0

			frappe.db.set_value(
				"Budget Line Item",
				row.name,
				{
					"actual_amount": flt(actual_amount),
					"variance": flt(row.budgeted_amount) - flt(actual_amount),
				},
				update_modified=False,
			)
