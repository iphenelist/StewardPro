# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TithesandOfferings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		campmeeting_offering: DF.Currency
		church_building_offering: DF.Currency
		date: DF.Date
		member: DF.Link | None
		naming_series: DF.Literal["TAO-.YYYY.-"]
		notes: DF.SmallText | None
		offering_amount: DF.Currency
		offering_to_church: DF.Currency
		offering_to_field: DF.Currency
		payment_mode: DF.Literal["Cash", "Mpesa", "Bank Transfer", "Other"]
		receipt_number: DF.Data | None
		tithe_amount: DF.Currency
		total_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		"""Validate Tithes and Offerings data"""
		self.calculate_offering_distribution()
		self.calculate_total_amount()
		self.validate_amounts()
	
	def calculate_offering_distribution(self):
		"""Calculate offering distribution based on SDA standards"""
		if self.offering_amount:
			# 58% to field, 42% to church
			self.offering_to_field = self.offering_amount * 0.58
			self.offering_to_church = self.offering_amount * 0.42
		else:
			self.offering_to_field = 0
			self.offering_to_church = 0
	
	def calculate_total_amount(self):
		"""Calculate total amount from all contributions"""
		total = 0
		
		if self.tithe_amount:
			total += self.tithe_amount
		
		if self.offering_amount:
			total += self.offering_amount
		
		if self.campmeeting_offering:
			total += self.campmeeting_offering
		
		if self.church_building_offering:
			total += self.church_building_offering
		
		self.total_amount = total
	
	def validate_amounts(self):
		"""Validate that amounts are positive"""
		if self.tithe_amount and self.tithe_amount < 0:
			frappe.throw("Tithe amount cannot be negative")
		
		if self.offering_amount and self.offering_amount < 0:
			frappe.throw("Offering amount cannot be negative")
		
		if self.campmeeting_offering and self.campmeeting_offering < 0:
			frappe.throw("Camp meeting offering cannot be negative")
		
		if self.church_building_offering and self.church_building_offering < 0:
			frappe.throw("Church building offering cannot be negative")
		
		if self.total_amount <= 0:
			frappe.throw("At least one contribution amount must be greater than zero")
	
	def before_submit(self):
		"""Actions before submitting the document"""
		if not self.receipt_number:
			self.receipt_number = self.generate_receipt_number()
	
	def generate_receipt_number(self):
		"""Generate a unique receipt number"""
		from datetime import datetime
		
		# Format: RCP-YYYY-MM-DD-XXXX
		date_str = datetime.now().strftime("%Y-%m-%d")
		
		# Get the count of receipts for today
		count = frappe.db.count("Tithes and Offerings", {
			"date": self.date,
			"docstatus": ["!=", 2]  # Exclude cancelled documents
		})
		
		receipt_number = f"RCP-{date_str}-{count + 1:04d}"
		return receipt_number
	
	def get_member_name(self):
		"""Get member's full name if member is specified"""
		if self.member:
			return frappe.db.get_value("Member", self.member, "full_name")
		return "Anonymous"

	def after_submit(self):
		"""Actions after submitting the document"""
		# Send receipt SMS if member has phone number
		if self.member:
			self.send_receipt_sms()

	def send_receipt_sms(self):
		"""Send receipt SMS to member"""
		try:
			# Get member details
			member_doc = frappe.get_doc("Member", self.member)

			if not member_doc.contact:
				frappe.logger().info(f"No phone number for member {member_doc.full_name}, skipping SMS")
				return

			from stewardpro.stewardpro.api.sms import send_tithe_offering_sms

			# Send SMS in background to avoid blocking the form
			frappe.enqueue(
				send_tithe_offering_sms,
				member_name=member_doc.full_name,
				phone_number=member_doc.contact,
				receipt_number=self.receipt_number,
				tithe_amount=self.tithe_amount,
				offering_amount=self.offering_amount,
				total_amount=self.total_amount,
				date=self.date,
				queue='short',
				timeout=60,
				is_async=True
			)

			frappe.msgprint(
				f"Receipt SMS will be sent to {member_doc.full_name} at {member_doc.contact}",
				title="SMS Notification",
				indicator="green"
			)

		except Exception as e:
			frappe.logger().error(f"Failed to queue receipt SMS for {self.name}: {str(e)}")
			# Don't block submission if SMS fails
			pass
	
	def get_tithe_percentage(self):
		"""Calculate tithe as percentage of total (for reporting)"""
		if self.total_amount and self.tithe_amount:
			return (self.tithe_amount / self.total_amount) * 100
		return 0
	
	def get_offering_percentage(self):
		"""Calculate offering as percentage of total (for reporting)"""
		if self.total_amount and self.offering_amount:
			return (self.offering_amount / self.total_amount) * 100
		return 0
