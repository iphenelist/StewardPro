# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DepartmentBudgetItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		budgeted_amount: DF.Currency
		description: DF.SmallText | None
		item: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity: DF.Float
		remaining_amount: DF.Currency
		spent_amount: DF.Currency
		unit_price: DF.Currency
	# end: auto-generated types

	def validate(self):
		"""Validate budget item"""
		self.validate_quantity()
		self.calculate_budgeted_amount()
		self.validate_item_department()
		self.calculate_remaining_amount()

	def validate_quantity(self):
		"""Validate quantity is positive"""
		if self.quantity <= 0:
			frappe.throw("Quantity must be greater than zero")

	def calculate_budgeted_amount(self):
		"""Calculate budgeted amount based on quantity and unit price"""
		if self.quantity and self.unit_price:
			self.budgeted_amount = self.quantity * self.unit_price
		else:
			self.budgeted_amount = 0

	def validate_item_department(self):
		"""Validate that the item belongs to the same department as the budget"""
		if self.item and self.parent:
			# Get the department from the parent Department Budget
			parent_doc = frappe.get_doc("Department Budget", self.parent)
			if parent_doc.department:
				# Get the item's department
				item_doc = frappe.get_doc("Item", self.item)
				if item_doc.department != parent_doc.department:
					frappe.throw(f"Item '{self.item}' belongs to department '{item_doc.department}' but this budget is for department '{parent_doc.department}'")

	def calculate_remaining_amount(self):
		"""Calculate remaining amount"""
		if not self.spent_amount:
			self.spent_amount = 0
		
		self.remaining_amount = self.budgeted_amount - self.spent_amount
