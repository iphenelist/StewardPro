# Copyright (c) 2025, Innocent P Metumba and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class SMSLog(Document):
	def autoname(self):
		"""Generate unique name using recipient name and timestamp"""
		if self.custom_recipient_name:
			# Create a unique name using recipient name and timestamp
			timestamp = now_datetime().strftime("%Y%m%d-%H%M%S")
			# Clean recipient name (remove spaces and special characters)
			clean_name = "".join(c for c in self.custom_recipient_name if c.isalnum() or c in (' ', '-', '_')).strip()
			clean_name = clean_name.replace(' ', '-')[:20]  # Limit length and replace spaces
			self.name = f"{clean_name}-{timestamp}"
		else:
			# Fallback to SMS type with timestamp if no recipient name
			timestamp = now_datetime().strftime("%Y%m%d-%H%M%S")
			sms_type = self.custom_sms_type or "SMS"
			clean_type = "".join(c for c in sms_type if c.isalnum() or c in (' ', '-', '_')).strip()
			clean_type = clean_type.replace(' ', '-')[:20]
			self.name = f"{clean_type}-{timestamp}"
