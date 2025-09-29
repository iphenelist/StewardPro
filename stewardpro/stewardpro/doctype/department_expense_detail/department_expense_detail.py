# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from stewardpro.stewardpro.doctype.department_expense.department_expense import DepartmentExpense

class DepartmentExpenseDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency | None
		expense_category: DF.Literal["Equipment", "Supplies", "Events", "Training", "Travel", "Utilities", "Maintenance", "Salaries", "Rent", "Insurance", "Other"]
		expense_description: DF.Data
		item: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity: DF.Float
		unit_price: DF.Currency
	# end: auto-generated types

	def validate(self):
		"""Validate expense detail"""
		self.validate_quantity()
		self.calculate_amount()
		self.validate_item_department()

	def validate_quantity(self):
		"""Validate quantity is positive"""
		if self.quantity <= 0:
			frappe.throw("Quantity must be greater than zero")

	def calculate_amount(self):
		"""Calculate amount based on quantity and unit price"""
		if self.quantity and self.unit_price:
			self.amount = self.quantity * self.unit_price
		else:
			self.amount = 0

	def validate_item_department(self):
		"""Validate that the item belongs to the same department as the expense"""
		if self.item and self.parent:
			# Get parent expense document
			parent_doc = frappe.get_doc("Department Expense", self.parent)
			if parent_doc.department:
				# Get item's department
				item_doc = frappe.get_doc("Item", self.item)
				if item_doc.department != parent_doc.department:
					frappe.throw(f"Item '{self.item}' belongs to department '{item_doc.department}' but this expense is for department '{parent_doc.department}'")
