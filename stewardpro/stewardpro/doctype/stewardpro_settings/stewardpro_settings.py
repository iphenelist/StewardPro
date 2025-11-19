# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_months, getdate, today
from datetime import datetime


class StewardProSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		enable_mobile_money_integration: DF.Check
		enable_sms_integration: DF.Check
		mobile_money_base_url: DF.Data | None
		money_api_key: DF.Password | None
		money_public_key: DF.Password | None
		sms_api_key: DF.Password | None
		sms_api_secret: DF.Password | None
		sms_base_url: DF.Data | None
		sms_sender_id: DF.Data | None
		supported_providers: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate StewardPro Settings"""
		pass


@frappe.whitelist()
def get_stewardpro_settings():
	"""Get StewardPro Settings singleton"""
	if not frappe.db.exists('StewardPro Settings', 'StewardPro Settings'):
		# Create default settings if not exists
		doc = frappe.get_doc({
			'doctype': 'StewardPro Settings'
		})
		doc.insert()
		return doc

	return frappe.get_single('StewardPro Settings')






