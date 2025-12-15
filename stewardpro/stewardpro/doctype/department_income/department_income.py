# Copyright (c) 2025, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DepartmentIncome(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		date: DF.Date
		department: DF.Link
		department_code: DF.Data | None
		description: DF.Text | None
		income_type: DF.Literal["Tithe", "Offering", "Donation", "Fund Raising", "Grant", "Other"]
		naming_series: DF.Literal["DI-.YYYY.-"]
		notes: DF.Text | None
		payment_mode: DF.Literal["Cash", "Cheque", "Bank Transfer", "Mpesa", "Credit Card", "Other"]
		receipt_number: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate Department Income"""
		self.validate_department()
		self.validate_amount()
		self.fetch_department_code()

	def validate_department(self):
		"""Ensure department exists and is active"""
		if self.department:
			dept = frappe.get_doc("Department", self.department)
			if not dept.is_active:
				frappe.throw(f"Department {self.department} is not active")

	def validate_amount(self):
		"""Ensure amount is positive"""
		if self.amount <= 0:
			frappe.throw("Amount must be greater than zero")

	def fetch_department_code(self):
		"""Fetch department code from department"""
		if self.department and not self.department_code:
			self.department_code = frappe.db.get_value("Department", self.department, "department_code")

	def on_submit(self):
		"""Actions on submit"""
		pass

	def on_cancel(self):
		"""Actions on cancel"""
		pass

