# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate


class Remittance(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from stewardpro.stewardpro.doctype.remittance_item.remittance_item import RemittanceItem

		approval_date: DF.Date | None
		approved_by: DF.Link | None
		contact_details: DF.SmallText | None
		contact_person: DF.Data | None
		naming_series: DF.Literal["REM-.YYYY.-"]
		notes: DF.Text | None
		offering_to_field_amount: DF.Currency
		organization_name: DF.Data
		organization_type: DF.Literal["Conference", "Union", "Division", "General Conference", "Other"]
		other_remittances_amount: DF.Currency
		payment_mode: DF.Literal["Bank Transfer", "Cheque", "Cash", "Other"]
		preparation_date: DF.Date | None
		prepared_by: DF.Link | None
		reference_number: DF.Data | None
		remittance_date: DF.Date
		remittance_items: DF.Table[RemittanceItem]
		remittance_period: DF.Literal["Weekly", "Monthly", "Quarterly", "Annual"]
		special_offerings_amount: DF.Currency
		status: DF.Literal["Draft", "Pending Approval", "Approved", "Sent", "Received"]
		tithe_amount: DF.Currency
		total_remittance_amount: DF.Currency
	# end: auto-generated types

	def validate(self):
		"""Validate Remittance"""
		self.calculate_total_amount()
		self.validate_amounts()
		self.validate_approval()
		self.populate_remittance_items()
	
	def calculate_total_amount(self):
		"""Calculate total remittance amount"""
		total = 0
		
		if self.tithe_amount:
			total += self.tithe_amount
		
		if self.offering_to_field_amount:
			total += self.offering_to_field_amount
		
		if self.special_offerings_amount:
			total += self.special_offerings_amount
		
		if self.other_remittances_amount:
			total += self.other_remittances_amount
		
		self.total_remittance_amount = total
	
	def validate_amounts(self):
		"""Validate remittance amounts"""
		if self.total_remittance_amount <= 0:
			frappe.throw("Total remittance amount must be greater than zero")
	
	def validate_approval(self):
		"""Validate approval requirements"""
		if self.status == "Approved" and not self.approved_by:
			frappe.throw("Approved By is required when status is Approved")
		
		if self.approved_by and not self.approval_date:
			self.approval_date = frappe.utils.today()
	
	def populate_remittance_items(self):
		"""Populate remittance items based on amounts"""
		self.remittance_items = []
		
		if self.tithe_amount:
			self.append("remittance_items", {
				"item_type": "Tithe",
				"description": "Tithe remittance (100%)",
				"amount": self.tithe_amount,
				"percentage": 100
			})
		
		if self.offering_to_field_amount:
			self.append("remittance_items", {
				"item_type": "Offering to Field",
				"description": "Regular offering to field (58%)",
				"amount": self.offering_to_field_amount,
				"percentage": 58
			})
		
		if self.special_offerings_amount:
			self.append("remittance_items", {
				"item_type": "Special Offering",
				"description": "Special offerings (Camp meeting, etc.)",
				"amount": self.special_offerings_amount,
				"percentage": 100
			})
		
		if self.other_remittances_amount:
			self.append("remittance_items", {
				"item_type": "Other",
				"description": "Other remittances",
				"amount": self.other_remittances_amount
			})
	
	def before_submit(self):
		"""Actions before submitting"""
		if self.status == "Draft":
			self.status = "Pending Approval"
	
	def on_submit(self):
		"""Actions on submit"""
		if self.status == "Pending Approval":
			self.status = "Approved"
	
	def on_cancel(self):
		"""Actions on cancel"""
		self.status = "Draft"
	
	def get_period_dates(self):
		"""Get the period dates for this remittance"""
		from frappe.utils import add_months, add_days
		
		base_date = getdate(self.remittance_date)
		
		if self.remittance_period == "Weekly":
			period_to = base_date
			period_from = add_days(period_to, -6)
		elif self.remittance_period == "Monthly":
			period_to = base_date
			period_from = add_months(period_to, -1)
		elif self.remittance_period == "Quarterly":
			period_to = base_date
			period_from = add_months(period_to, -3)
		elif self.remittance_period == "Annual":
			period_to = base_date
			period_from = add_months(period_to, -12)
		else:
			period_from = period_to = base_date
		
		return period_from, period_to
	
	def get_source_contributions(self):
		"""Get the source contributions for this remittance period"""
		period_from, period_to = self.get_period_dates()
		
		# Get tithes and offerings for the period
		contributions = frappe.db.sql("""
			SELECT 
				SUM(tithe_amount) as total_tithe,
				SUM(offering_to_field) as total_offering_to_field,
				SUM(campmeeting_offering + church_building_offering) as total_special_offerings
			FROM `tabTithes and Offerings`
			WHERE date BETWEEN %s AND %s
			AND docstatus = 1
		""", (period_from, period_to), as_dict=True)
		
		return contributions[0] if contributions else {}
	
	def auto_populate_amounts(self):
		"""Auto-populate amounts from source contributions"""
		contributions = self.get_source_contributions()
		
		if contributions:
			self.tithe_amount = contributions.get("total_tithe", 0)
			self.offering_to_field_amount = contributions.get("total_offering_to_field", 0)
			self.special_offerings_amount = contributions.get("total_special_offerings", 0)
		
		self.calculate_total_amount()
	
	def get_remittance_summary(self):
		"""Get a summary of this remittance"""
		period_from, period_to = self.get_period_dates()
		
		summary = {
			"remittance_number": self.name,
			"organization": self.organization_name,
			"period_from": period_from,
			"period_to": period_to,
			"total_amount": self.total_remittance_amount,
			"status": self.status,
			"items": []
		}
		
		for item in self.remittance_items:
			summary["items"].append({
				"type": item.item_type,
				"description": item.description,
				"amount": item.amount,
				"percentage": item.percentage
			})
		
		return summary
