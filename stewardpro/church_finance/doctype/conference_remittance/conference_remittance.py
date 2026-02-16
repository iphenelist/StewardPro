# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ConferenceRemittance(Document):
	def before_save(self):
		self.total_remittance = sum(flt(item.amount) for item in self.items)
