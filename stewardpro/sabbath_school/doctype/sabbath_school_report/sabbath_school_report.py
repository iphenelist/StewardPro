# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SabbathSchoolReport(Document):
	def before_save(self):
		self.grand_total_offering = (
			flt(self.total_regular_offering) +
			flt(self.total_thirteenth_sabbath) +
			flt(self.total_investment) +
			flt(self.total_birthday_thanksgiving)
		)
