# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DepartmentExpense(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from stewardpro.church_management.doctype.department_expense_detail.department_expense_detail import DepartmentExpenseDetail

		approval_date: DF.Date | None
		approved_by: DF.Link | None
		attachments: DF.Attach | None
		budget_reference: DF.Link | None
		department: DF.Link
		expense_date: DF.Date
		expense_details: DF.Table[DepartmentExpenseDetail]
		invoice_number: DF.Data | None
		naming_series: DF.Literal["EXP-.YYYY.-"]
		notes: DF.Text | None
		payment_mode: DF.Literal["Cash", "Cheque", "Bank Transfer", "Mpesa", "Credit Card", "Other"]
		receipt_number: DF.Data | None
		reference_number: DF.Data | None
		status: DF.Literal["Draft", "Pending Approval", "Approved", "Paid", "Rejected"]
		total_amount: DF.Currency | None
		vendor_supplier: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate Department Expense"""
		self.validate_expense_details()
		self.calculate_total_amount()
		self.validate_budget_reference()
		self.validate_approval()
	
	def validate_expense_details(self):
		"""Validate expense details"""
		if not self.expense_details:
			frappe.throw("At least one expense detail is required")

		for detail in self.expense_details:
			if detail.quantity <= 0:
				frappe.throw(f"Quantity must be greater than zero for item: {detail.expense_description}")
			if detail.unit_price <= 0:
				frappe.throw(f"Unit price must be greater than zero for item: {detail.expense_description}")

	def calculate_total_amount(self):
		"""Calculate total amount from expense details"""
		total = 0
		for detail in self.expense_details:
			if detail.quantity and detail.unit_price:
				detail.amount = detail.quantity * detail.unit_price
				total += detail.amount
		self.total_amount = total
	
	def validate_budget_reference(self):
		"""Validate budget reference and check budget availability"""
		if self.budget_reference:
			budget = frappe.get_doc("Department Budget", self.budget_reference)

			# Check if budget is active
			if not budget.is_active:
				frappe.throw(f"Budget {self.budget_reference} is not active")

			# Check if department matches
			if budget.department != self.department:
				frappe.throw(f"Department mismatch. Budget is for {budget.department}, expense is for {self.department}")

			# Check budget availability (if budget has remaining_amount field)
			if hasattr(budget, 'remaining_amount') and budget.remaining_amount is not None:
				if budget.remaining_amount < self.total_amount:
					frappe.msgprint(
						f"Warning: This expense ({self.total_amount}) exceeds remaining budget ({budget.remaining_amount})",
						alert=True
					)
			elif hasattr(budget, 'total_budget_amount') and budget.total_budget_amount:
				# Calculate remaining amount if not available
				spent_amount = self.get_total_spent_for_budget(budget.name)
				remaining = budget.total_budget_amount - spent_amount
				if remaining < self.total_amount:
					frappe.msgprint(
						f"Warning: This expense ({self.total_amount}) exceeds remaining budget ({remaining})",
						alert=True
					)
	
	def get_total_spent_for_budget(self, budget_name):
		"""Calculate total amount spent for a specific budget"""
		from frappe.query_builder import DocType
		from frappe.query_builder.functions import Sum

		Expense = DocType("Department Expense")

		result = (
			frappe.qb.from_(Expense)
			.select(Sum(Expense.total_amount).as_("total_spent"))
			.where(Expense.budget_reference == budget_name)
			.where(Expense.docstatus == 1)
			.where(Expense.name != self.name)  # Exclude current expense
		).run(as_dict=True)

		return result[0].total_spent or 0 if result else 0

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

	@frappe.whitelist()
	def get_budget_items(self, budget_reference):
		"""Get budget items for the selected budget reference"""
		if not budget_reference:
			return []

		budget = frappe.get_doc("Department Budget", budget_reference)
		budget_items = []

		for item in budget.budget_items:
			budget_items.append({
				"item": item.item,
				"item_name": frappe.db.get_value("Item", item.item, "item_name"),
				"category": item.category,
				"description": item.description,
				"quantity": item.quantity,
				"unit_price": item.unit_price,
				"budgeted_amount": item.budgeted_amount,
				"spent_amount": item.spent_amount or 0,
				"remaining_amount": item.remaining_amount or item.budgeted_amount
			})

		return budget_items


@frappe.whitelist()
def get_budget_items_for_reference(budget_reference):
	"""Get budget items for the selected budget reference - static method"""
	if not budget_reference:
		return []

	budget = frappe.get_doc("Department Budget", budget_reference)
	budget_items = []

	for item in budget.budget_items:
		budget_items.append({
			"item": item.item,
			"item_name": frappe.db.get_value("Item", item.item, "item_name"),
			"category": item.category,
			"description": item.description,
			"quantity": item.quantity,
			"unit_price": item.unit_price,
			"budgeted_amount": item.budgeted_amount,
			"spent_amount": item.spent_amount or 0,
			"remaining_amount": item.remaining_amount or item.budgeted_amount
		})

	return budget_items

def update_budget_spent_amount(self, reverse=False):
		"""Update the spent amount in the related budget"""
		if not self.budget_reference:
			return

		budget = frappe.get_doc("Department Budget", self.budget_reference)

		# Process each expense detail
		for expense_detail in self.expense_details:
			# Find matching budget item by category
			for budget_item in budget.budget_items:
				if budget_item.category == expense_detail.expense_category:
					if reverse:
						budget_item.spent_amount = (budget_item.spent_amount or 0) - expense_detail.amount
					else:
						budget_item.spent_amount = (budget_item.spent_amount or 0) + expense_detail.amount

					budget_item.remaining_amount = budget_item.budgeted_amount - budget_item.spent_amount
					break

		# Recalculate budget totals
		if hasattr(budget, 'calculate_spent_amount'):
			budget.calculate_spent_amount()
		if hasattr(budget, 'calculate_remaining_amount'):
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
		"current_spent": budget.spent_amount if hasattr(budget, 'spent_amount') else 0,
		"remaining_before": budget.remaining_amount if hasattr(budget, 'remaining_amount') else budget.total_budget_amount,
		"remaining_after": (budget.remaining_amount if hasattr(budget, 'remaining_amount') else budget.total_budget_amount) - self.total_amount,
		"utilization_before": budget.get_budget_utilization_percentage() if hasattr(budget, 'get_budget_utilization_percentage') else 0,
		"utilization_after": ((budget.spent_amount if hasattr(budget, 'spent_amount') else 0) + self.total_amount) / budget.total_budget_amount * 100 if budget.total_budget_amount else 0
	}

	return impact

def is_over_budget(self):
	"""Check if this expense will cause budget overrun"""
	if not self.budget_reference:
		return False

	budget = frappe.get_doc("Department Budget", self.budget_reference)
	current_spent = budget.spent_amount if hasattr(budget, 'spent_amount') else 0
	return (current_spent + self.total_amount) > budget.total_budget_amount
