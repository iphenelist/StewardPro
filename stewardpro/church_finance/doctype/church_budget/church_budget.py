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
