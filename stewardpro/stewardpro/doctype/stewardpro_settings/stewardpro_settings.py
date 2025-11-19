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

		admin_contact_email: DF.Data | None
		admin_contact_name: DF.Data | None
		admin_contact_phone: DF.Data | None
		airtel_money_api_key: DF.Password | None
		api_calls_per_month: DF.Int
		backup_frequency: DF.Literal["Daily", "Weekly", "Monthly"]
		billing_contact_email: DF.Data | None
		current_member_count: DF.Int
		data_retention_months: DF.Int
		dedicated_support: DF.Check
		enable_mobile_money_integration: DF.Check
		enable_sms_integration: DF.Check
		export_limit_per_month: DF.Int
		max_budget_items: DF.Int
		max_departments: DF.Int
		max_members: DF.Int
		max_reports_per_month: DF.Int
		mobile_money_monthly_cost: DF.Currency
		mobile_money_transaction_fee: DF.Percent
		mpesa_api_key: DF.Password | None
		mpesa_public_key: DF.Password | None
		notification_email: DF.Data | None
		notify_on_limit_reached: DF.Check
		onsite_training: DF.Check
		priority_support: DF.Check
		send_usage_reports: DF.Check
		sms_api_key: DF.Password | None
		sms_api_secret: DF.Password | None
		sms_cost_per_message: DF.Currency
		sms_monthly_quota: DF.Int
		sms_provider: DF.Literal["Beem Africa", "Other"]
		sms_sender_id: DF.Data | None
		sms_used_this_month: DF.Int
		storage_limit_gb: DF.Int
		supported_providers: DF.Literal["M-Pesa Only", "M-Pesa + Tigo Pesa", "All Providers (M-Pesa, Tigo Pesa, Airtel Money, HaloPesa)"]
		tigo_pesa_api_key: DF.Password | None
		usage_report_frequency: DF.Literal["Weekly", "Monthly", "Quarterly"]
	# end: auto-generated types

	def validate(self):
		"""Validate StewardPro Settings"""
		self.validate_email_addresses()
		self.update_member_count()

	def validate_email_addresses(self):
		"""Validate email address formats"""
		import re
		email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		
		email_fields = [
			('notification_email', 'Notification Email'),
			('admin_contact_email', 'Admin Contact Email'),
			('billing_contact_email', 'Billing Contact Email')
		]
		
		for field, label in email_fields:
			email = getattr(self, field, None)
			if email and not re.match(email_pattern, email):
				frappe.throw(f"Please enter a valid {label}")



	def update_member_count(self):
		"""Update current member count"""
		try:
			self.current_member_count = frappe.db.count('Member', {'status': "Active"})
		except:
			self.current_member_count = 0



	def is_feature_enabled(self, feature):
		"""Check if a specific feature is enabled"""
		feature_map = {
			'sms': self.enable_sms_integration,
			'mobile_money': self.enable_mobile_money_integration
		}

		return bool(feature_map.get(feature, False))

	def get_sms_balance(self):
		"""Get remaining SMS balance for current month"""
		if not self.enable_sms_integration:
			return 0
		return max(0, self.sms_monthly_quota - self.sms_used_this_month)

	def can_send_sms(self, count=1):
		"""Check if SMS can be sent"""
		if not self.is_feature_enabled('sms'):
			return False, "SMS integration is not enabled"
		
		balance = self.get_sms_balance()
		if balance < count:
			return False, f"Insufficient SMS balance. Available: {balance}, Required: {count}"
		
		return True, "OK"

	def increment_sms_usage(self, count=1):
		"""Increment SMS usage counter"""
		self.sms_used_this_month = (self.sms_used_this_month or 0) + count
		self.save()

	def reset_monthly_counters(self):
		"""Reset monthly usage counters (called by scheduled job)"""
		self.sms_used_this_month = 0
		self.save()


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


@frappe.whitelist()
def check_feature_access(feature):
	"""Check if a feature is accessible"""
	settings = get_stewardpro_settings()
	return settings.is_feature_enabled(feature)


@frappe.whitelist()
def get_sms_status():
	"""Get SMS usage status"""
	settings = get_stewardpro_settings()
	return {
		'enabled': settings.enable_sms_integration,
		'quota': settings.sms_monthly_quota,
		'used': settings.sms_used_this_month,
		'balance': settings.get_sms_balance(),
		'can_send': settings.can_send_sms()[0]
	}


def reset_monthly_counters_job():
	"""Scheduled job to reset monthly counters"""
	try:
		settings = get_stewardpro_settings()
		settings.reset_monthly_counters()
		frappe.logger().info("Monthly counters reset successfully")
	except Exception as e:
		frappe.logger().error(f"Failed to reset monthly counters: {str(e)}")
