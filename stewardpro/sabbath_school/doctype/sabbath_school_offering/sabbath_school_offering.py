# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SabbathSchoolOffering(Document):
	def before_save(self):
		self.calculate_total()

	def calculate_total(self):
		self.total_offering = (
			flt(self.regular_offering) +
			flt(self.thirteenth_sabbath) +
			flt(self.investment) +
			flt(self.birthday_thanksgiving)
		)
