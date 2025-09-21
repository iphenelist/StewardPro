# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DepartmentBudget(Document):

	def validate(self):
		"""Validate Department Budget"""
		self.calculate_allocated_amount()
		self.calculate_spent_amount()
		self.calculate_remaining_amount()
		self.validate_budget_items()
	
	def calculate_allocated_amount(self):
		"""Calculate total allocated amount from budget items"""
		total = 0
		for item in self.budget_items:
			if item.budgeted_amount:
				total += item.budgeted_amount
		
		self.allocated_amount = total
	
	def calculate_spent_amount(self):
		"""Calculate total spent amount from expenses"""
		# This will be calculated from Expense doctype when implemented
		total = 0
		for item in self.budget_items:
			if item.spent_amount:
				total += item.spent_amount
		
		self.spent_amount = total
	
	def calculate_remaining_amount(self):
		"""Calculate remaining budget amount"""
		self.remaining_amount = self.total_budget_amount - self.spent_amount
	
	def validate_budget_items(self):
		"""Validate budget items"""
		if not self.budget_items:
			frappe.throw("At least one budget item is required")
		
		if self.allocated_amount > self.total_budget_amount:
			frappe.throw(f"Allocated amount ({self.allocated_amount}) cannot exceed total budget amount ({self.total_budget_amount})")
	
	def get_budget_utilization_percentage(self):
		"""Calculate budget utilization percentage"""
		if self.total_budget_amount:
			return (self.spent_amount / self.total_budget_amount) * 100
		return 0
	
	def get_allocation_percentage(self):
		"""Calculate allocation percentage"""
		if self.total_budget_amount:
			return (self.allocated_amount / self.total_budget_amount) * 100
		return 0
	
	def is_over_budget(self):
		"""Check if budget is over spent"""
		return self.spent_amount > self.total_budget_amount
	
	def get_budget_status_color(self):
		"""Get color code for budget status"""
		utilization = self.get_budget_utilization_percentage()
		
		if utilization <= 50:
			return "green"
		elif utilization <= 80:
			return "orange"
		else:
			return "red"
	
	def on_submit(self):
		"""Actions on submit"""
		self.is_active = 1
	