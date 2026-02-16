# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint


class SabbathSchoolAttendance(Document):
	def before_save(self):
		self.total_present = cint(self.members_present) + cint(self.visitors)
