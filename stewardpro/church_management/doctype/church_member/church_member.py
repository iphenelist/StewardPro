# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchMember(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		baptism_date: DF.Date | None
		city: DF.Data | None
		contact: DF.Phone | None
		date_of_birth: DF.Date | None
		email: DF.Data | None
		emergency_contact_name: DF.Data | None
		emergency_contact_phone: DF.Phone | None
		employer: DF.Data | None
		full_name: DF.Data
		gender: DF.Literal["", "Male", "Female"]
		member_id: DF.Data
		membership_date: DF.Date | None
		notes: DF.Text | None
		occupation: DF.Data | None
		relationship: DF.Data | None
		role: DF.Literal["", "Member", "Elder", "Deacon", "Deaconess", "Treasurer", "Clerk", "Pastor", "Associate Pastor", "Choir Director", "Sabbath School Superintendent", "Youth Leader", "Children's Ministry Leader", "Community Services Leader"]
		skills_talents: DF.SmallText | None
		status: DF.Literal["Active", "Inactive", "Transferred", "Deceased"]
	# end: auto-generated types

	def validate(self):
		"""Validate Church Member data"""
		self.validate_member_id()
		self.validate_contact()
		self.validate_dates()
	
	def validate_member_id(self):
		"""Ensure member ID is unique and properly formatted"""
		if not self.member_id:
			frappe.throw("Member ID is required")
		
		# Check for duplicate member ID
		existing = frappe.db.exists("Church Member", {"member_id": self.member_id, "name": ["!=", self.name]})
		if existing:
			frappe.throw(f"Member ID {self.member_id} already exists")
	
	def validate_contact(self):
		"""Validate contact information format"""
		if self.contact:
			# Basic validation for contact format
			if len(self.contact) < 10:
				frappe.msgprint("Contact number seems too short", alert=True)
		
		if self.email:
			# Basic email validation
			import re
			email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
			if not re.match(email_pattern, self.email):
				frappe.throw("Please enter a valid email address")
	
	def validate_dates(self):
		"""Validate date fields"""
		from datetime import date
		
		if self.date_of_birth and self.date_of_birth > date.today():
			frappe.throw("Date of birth cannot be in the future")
		
		if self.baptism_date and self.baptism_date > date.today():
			frappe.throw("Baptism date cannot be in the future")
		
		if self.membership_date and self.membership_date > date.today():
			frappe.throw("Membership date cannot be in the future")
		
		if self.date_of_birth and self.baptism_date:
			if self.baptism_date < self.date_of_birth:
				frappe.throw("Baptism date cannot be before date of birth")
	
	def get_full_display_name(self):
		"""Return full display name with role"""
		if self.role and self.role != "Member":
			return f"{self.full_name} ({self.role})"
		return self.full_name
	
	def get_age(self):
		"""Calculate and return member's age"""
		if not self.date_of_birth:
			return None
		
		from datetime import date
		today = date.today()
		age = today.year - self.date_of_birth.year
		
		# Adjust if birthday hasn't occurred this year
		if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
			age -= 1
		
		return age
	
	def is_active(self):
		"""Check if member is active"""
		return self.status == "Active"
