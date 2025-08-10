# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class DepartmentBudgetItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		budgeted_amount: DF.Currency
		category: DF.Literal["Equipment", "Supplies", "Events", "Training", "Travel", "Utilities", "Maintenance", "Other"]
		description: DF.SmallText | None
		item_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remaining_amount: DF.Currency
		spent_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		"""Validate budget item"""
		self.calculate_remaining_amount()
	
	def calculate_remaining_amount(self):
		"""Calculate remaining amount"""
		if not self.spent_amount:
			self.spent_amount = 0
		
		self.remaining_amount = self.budgeted_amount - self.spent_amount
