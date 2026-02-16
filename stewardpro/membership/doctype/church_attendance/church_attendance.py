# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint


class ChurchAttendance(Document):
	def before_save(self):
		self.total_attendance = cint(self.total_adults) + cint(self.total_children) + cint(self.total_visitors)
