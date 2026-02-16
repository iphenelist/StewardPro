# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class TitheandOfferingEntry(Document):
	def before_save(self):
		self.calculate_totals()

	def calculate_totals(self):
		self.total_tithe = 0
		self.total_offerings = 0
		for item in self.items:
			offering_type = frappe.db.get_value("Offering Type", item.offering_type, "offering_category")
			if offering_type == "Tithe":
				self.total_tithe += flt(item.amount)
			else:
				self.total_offerings += flt(item.amount)
		self.grand_total = flt(self.total_tithe) + flt(self.total_offerings)
