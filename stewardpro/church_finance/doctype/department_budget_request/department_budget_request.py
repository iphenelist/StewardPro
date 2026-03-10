# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, today, getdate


class DepartmentBudgetRequest(Document):
	def before_save(self):
		self.calculate_totals()

	def validate(self):
		self.validate_items()

	def validate_items(self):
		for item in self.items:
			if flt(item.amount) <= 0:
				frappe.throw(f"Amount must be greater than zero for item: {item.expense_description}")
			# Auto-calculate amount from qty * unit_cost if both provided
			if flt(item.quantity) and flt(item.unit_cost):
				item.amount = flt(item.quantity) * flt(item.unit_cost)

	def calculate_totals(self):
		self.total_requested_amount = sum(flt(item.amount) for item in self.items)

	def on_submit(self):
		self.status = "Pending Approval"
		self.create_church_budget()

	def on_cancel(self):
		self.status = "Draft"
		if self.church_budget:
			budget = frappe.get_doc("Church Budget", self.church_budget)
			if budget.docstatus == 0:
				budget.delete()
			self.db_set("church_budget", "")

	def create_church_budget(self):
		"""Create a Church Budget record from this department request"""
		budget_name = f"{self.department} Budget - {self.fiscal_year} {self.budget_period}"

		budget = frappe.new_doc("Church Budget")
		budget.budget_name = budget_name
		budget.budget_year = self.fiscal_year
		budget.budget_period = self.budget_period

		# Set period dates based on fiscal year and period
		year = self.fiscal_year
		period_dates = {
			"Annual": (f"{year}-01-01", f"{year}-12-31"),
			"Q1": (f"{year}-01-01", f"{year}-03-31"),
			"Q2": (f"{year}-04-01", f"{year}-06-30"),
			"Q3": (f"{year}-07-01", f"{year}-09-30"),
			"Q4": (f"{year}-10-01", f"{year}-12-31"),
		}
		start, end = period_dates.get(self.budget_period, (f"{year}-01-01", f"{year}-12-31"))
		budget.start_date = start
		budget.end_date = end

		# Add expense items from department request
		for item in self.items:
			budget.append("expense_items", {
				"account": item.account,
				"description": f"[{self.department}] {item.expense_description}",
				"budgeted_amount": flt(item.amount),
			})

		budget.department_budget_request = self.name
		budget.remarks = f"Auto-created from Department Budget Request: {self.name}"
		budget.insert(ignore_permissions=True)

		self.db_set("church_budget", budget.name)
		self.db_set("status", "Budgeted")

		frappe.msgprint(
			f"Church Budget <b>{budget.name}</b> has been created.",
			title="Budget Created",
			indicator="green"
		)
