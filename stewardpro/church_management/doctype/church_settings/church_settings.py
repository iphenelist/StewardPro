# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		auto_submit_remittance: DF.Check
		bank_details: DF.SmallText | None
		church_address: DF.SmallText | None
		church_contact: DF.Phone | None
		church_email: DF.Data | None
		church_name: DF.Data
		default_contact_details: DF.SmallText | None
		default_contact_person: DF.Data | None
		default_organization_name: DF.Data
		default_organization_type: DF.Literal["Conference", "Union", "Division", "General Conference", "Other"]
		default_payment_mode: DF.Literal["Bank Transfer", "Cheque", "Cash", "Other"]
		enable_automatic_remittance: DF.Check
		notification_email: DF.Data | None
		notify_on_remittance_creation: DF.Check
		reference_prefix: DF.Data | None
		remittance_day_of_month: DF.Int
		remittance_frequency: DF.Literal["", "Monthly", "Weekly"]
		send_remittance_summary: DF.Check
		summary_recipients: DF.SmallText | None
	# end: auto-generated types

	def validate(self):
		"""Validate Church Settings"""
		self.validate_remittance_day()
		self.validate_email_addresses()
	
	def validate_remittance_day(self):
		"""Validate remittance day of month"""
		if self.remittance_frequency == "Monthly" and self.remittance_day_of_month:
			if self.remittance_day_of_month < 1 or self.remittance_day_of_month > 28:
				frappe.throw("Remittance day of month must be between 1 and 28")
	
	def validate_email_addresses(self):
		"""Validate email address formats"""
		import re
		email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		
		if self.church_email and not re.match(email_pattern, self.church_email):
			frappe.throw("Please enter a valid church email address")
		
		if self.notification_email and not re.match(email_pattern, self.notification_email):
			frappe.throw("Please enter a valid notification email address")
		
		if self.summary_recipients:
			# Validate comma-separated email addresses
			emails = [email.strip() for email in self.summary_recipients.split(",")]
			for email in emails:
				if email and not re.match(email_pattern, email):
					frappe.throw(f"Invalid email address in summary recipients: {email}")
	
	def get_organization_settings(self):
		"""Get organization settings for remittance creation"""
		return {
			"organization_type": self.default_organization_type,
			"organization_name": self.default_organization_name,
			"contact_person": self.default_contact_person,
			"contact_details": self.default_contact_details,
			"default_payment_mode": self.default_payment_mode,
			"auto_submit_remittance": self.auto_submit_remittance,
			"bank_details": self.bank_details,
			"reference_prefix": self.reference_prefix or "REM"
		}
	
	def should_create_automatic_remittance(self):
		"""Check if automatic remittance should be created"""
		return self.enable_automatic_remittance
	
	def get_notification_settings(self):
		"""Get notification settings"""
		return {
			"notify_on_creation": self.notify_on_remittance_creation,
			"notification_email": self.notification_email,
			"send_summary": self.send_remittance_summary,
			"summary_recipients": self.summary_recipients
		}
