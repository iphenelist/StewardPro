# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from stewardpro.api.sms import send_tithe_offering_receipt


class TitheandOfferingEntry(Document):
	def before_save(self):
		self.calculate_offering_split()
		self.calculate_totals()

	def validate(self):
		self.validate_amounts()

	def on_submit(self):
		send_tithe_offering_receipt(self)

	def validate_amounts(self):
		for field in ("tithe", "offering", "camp_meeting", "church_building_fund"):
			if flt(self.get(field)) < 0:
				frappe.throw(f"{frappe.unscrub(field)} cannot be negative")

	def calculate_offering_split(self):
		"""Split offering: 42% stays local, 56% goes to conference"""
		offering = flt(self.offering)
		self.offering_local_share = 42
		self.offering_conference_share = 56
		self.offering_local_amount = flt(offering * 42 / 100, 2)
		self.offering_conference_amount = flt(offering * 56 / 100, 2)

	def calculate_totals(self):
		"""Calculate all totals based on flat fields"""
		tithe = flt(self.tithe)
		offering = flt(self.offering)
		camp_meeting = flt(self.camp_meeting)
		building_fund = flt(self.church_building_fund)

		self.total_tithe_and_offerings = tithe + offering + camp_meeting + building_fund

		# Conference gets: 100% tithe + 56% offering + 100% camp meeting
		self.total_for_conference = tithe + flt(self.offering_conference_amount) + camp_meeting

		# Local church gets: 42% offering + 100% building fund
		self.total_for_local_church = flt(self.offering_local_amount) + building_fund

		self.grand_total = self.total_for_conference + self.total_for_local_church
