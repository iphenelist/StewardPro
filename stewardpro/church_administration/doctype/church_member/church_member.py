# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from stewardpro.api.sms import send_member_welcome


class ChurchMember(Document):
	def before_save(self):
		self.set_full_name()

	def set_full_name(self):
		parts = [self.first_name, self.middle_name, self.last_name]
		self.full_name = " ".join([p for p in parts if p])

	def after_insert(self):
		send_member_welcome(self)
