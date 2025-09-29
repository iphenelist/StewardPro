# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Item(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category: DF.Literal["Equipment", "Supplies", "Events", "Training", "Travel", "Utilities", "Maintenance", "Salaries", "Rent", "Insurance", "Other"]
		department: DF.Link
		description: DF.Text | None
		is_active: DF.Check
		item_name: DF.Data
		notes: DF.Text | None
		standard_cost: DF.Currency
		unit_of_measure: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate Item"""
		self.validate_item_name()
		self.validate_department()
	
	def validate_item_name(self):
		"""Validate item name is unique"""
		if not self.item_name:
			frappe.throw("Item Name is required")
		
		# Check for duplicate item names
		existing = frappe.db.exists("Item", {"item_name": self.item_name, "name": ["!=", self.name]})
		if existing:
			frappe.throw(f"Item with name '{self.item_name}' already exists")
	
	def validate_department(self):
		"""Validate department exists and is active"""
		if self.department:
			dept = frappe.get_doc("Department", self.department)
			if not dept.is_active:
				frappe.throw(f"Department '{self.department}' is not active")
	
	def before_save(self):
		"""Actions before saving"""
		# Ensure item name is properly formatted
		if self.item_name:
			self.item_name = self.item_name.strip()


@frappe.whitelist()
def get_items_by_department(department, category=None):
	"""Get active items filtered by department and optionally by category"""
	filters = {
		"department": department,
		"is_active": 1
	}
	
	if category:
		filters["category"] = category
	
	return frappe.get_all(
		"Item",
		filters=filters,
		fields=["name", "item_name", "category", "standard_cost", "unit_of_measure"],
		order_by="item_name"
	)


@frappe.whitelist()
def get_items_by_category(category, department=None):
	"""Get active items filtered by category and optionally by department"""
	filters = {
		"category": category,
		"is_active": 1
	}
	
	if department:
		filters["department"] = department
	
	return frappe.get_all(
		"Item",
		filters=filters,
		fields=["name", "item_name", "department", "standard_cost", "unit_of_measure"],
		order_by="item_name"
	)


@frappe.whitelist()
def get_active_items():
	"""Get all active items"""
	return frappe.get_all(
		"Item",
		filters={"is_active": 1},
		fields=["name", "item_name", "category", "department", "standard_cost"],
		order_by="item_name"
	)
