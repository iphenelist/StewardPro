# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MembershipTransfer(Document):
	def on_submit(self):
		if self.transfer_type == "Transfer Out":
			frappe.db.set_value("Church Member", self.member, "membership_status", "Transferred Out")
		elif self.transfer_type == "Transfer In":
			frappe.db.set_value("Church Member", self.member, "membership_status", "Active")
			frappe.db.set_value("Church Member", self.member, "how_joined", "Transfer In")

	def on_cancel(self):
		if self.transfer_type == "Transfer Out":
			frappe.db.set_value("Church Member", self.member, "membership_status", "Active")
