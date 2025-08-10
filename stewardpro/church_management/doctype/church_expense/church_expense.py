# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchExpense(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		approval_date: DF.Date | None
		approved_by: DF.Link | None
		attachments: DF.Attach | None
		budget_reference: DF.Link | None
		department: DF.Literal["Sabbath School", "Youth Ministry", "Children's Ministry", "Music Ministry", "Community Services", "Women's Ministry", "Men's Ministry", "Health Ministry", "Education Ministry", "Evangelism", "Stewardship", "Family Life", "Communication", "Maintenance", "General", "Other"]
		expense_category: DF.Literal["Equipment", "Supplies", "Events", "Training", "Travel", "Utilities", "Maintenance", "Salaries", "Rent", "Insurance", "Other"]
		expense_date: DF.Date
		expense_description: DF.Data
		invoice_number: DF.Data | None
		naming_series: DF.Literal["EXP-.YYYY.-"]
		notes: DF.Text | None
		payment_mode: DF.Literal["Cash", "Cheque", "Bank Transfer", "Mpesa", "Credit Card", "Other"]
		receipt_number: DF.Data | None
		reference_number: DF.Data | None
		status: DF.Literal["Draft", "Pending Approval", "Approved", "Paid", "Rejected"]
		vendor_supplier: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate Church Expense"""
		self.validate_amount()
		self.validate_budget_reference()
		self.validate_approval()
	
	def validate_amount(self):
		"""Validate expense amount"""
		if self.amount <= 0:
			frappe.throw("Expense amount must be greater than zero")
	
	def validate_budget_reference(self):
		"""Validate budget reference and check budget availability"""
		if self.budget_reference:
			budget = frappe.get_doc("Department Budget", self.budget_reference)
			
			# Check if budget is active
			if budget.status != "Active":
				frappe.throw(f"Budget {self.budget_reference} is not active")
			
			# Check if department matches
			if budget.department != self.department:
				frappe.throw(f"Department mismatch. Budget is for {budget.department}, expense is for {self.department}")
			
			# Check budget availability
			if budget.remaining_amount < self.amount:
				frappe.msgprint(
					f"Warning: This expense ({self.amount}) exceeds remaining budget ({budget.remaining_amount})",
					alert=True
				)
	
	def validate_approval(self):
		"""Validate approval requirements"""
		if self.status == "Approved" and not self.approved_by:
			frappe.throw("Approved By is required when status is Approved")
		
		if self.approved_by and not self.approval_date:
			self.approval_date = frappe.utils.today()
	
	def before_submit(self):
		"""Actions before submitting"""
		if self.status == "Draft":
			self.status = "Pending Approval"
	
	def on_submit(self):
		"""Actions on submit"""
		self.update_budget_spent_amount()
	
	def on_cancel(self):
		"""Actions on cancel"""
		self.update_budget_spent_amount(reverse=True)
		self.status = "Draft"
	
	def update_budget_spent_amount(self, reverse=False):
		"""Update the spent amount in the related budget"""
		if not self.budget_reference:
			return
		
		budget = frappe.get_doc("Department Budget", self.budget_reference)
		
		# Find matching budget item
		for item in budget.budget_items:
			if item.category == self.expense_category:
				if reverse:
					item.spent_amount = (item.spent_amount or 0) - self.amount
				else:
					item.spent_amount = (item.spent_amount or 0) + self.amount
				
				item.remaining_amount = item.budgeted_amount - item.spent_amount
				break
		
		# Recalculate budget totals
		budget.calculate_spent_amount()
		budget.calculate_remaining_amount()
		budget.save()
	
	def get_budget_impact(self):
		"""Get the impact of this expense on the budget"""
		if not self.budget_reference:
			return None
		
		budget = frappe.get_doc("Department Budget", self.budget_reference)
		
		impact = {
			"budget_name": budget.name,
			"budget_total": budget.total_budget_amount,
			"current_spent": budget.spent_amount,
			"remaining_before": budget.remaining_amount,
			"remaining_after": budget.remaining_amount - self.amount,
			"utilization_before": budget.get_budget_utilization_percentage(),
			"utilization_after": ((budget.spent_amount + self.amount) / budget.total_budget_amount) * 100
		}
		
		return impact
	
	def is_over_budget(self):
		"""Check if this expense will cause budget overrun"""
		if not self.budget_reference:
			return False
		
		budget = frappe.get_doc("Department Budget", self.budget_reference)
		return (budget.spent_amount + self.amount) > budget.total_budget_amount
