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
		annual_cost: DF.Currency
		api_calls_per_month: DF.Int
		backup_frequency: DF.Literal["Daily", "Weekly", "Monthly"]
		billing_contact_email: DF.Data | None
		current_member_count: DF.Int
		data_retention_months: DF.Int
		dedicated_support: DF.Check
		enable_advanced_analytics: DF.Check
		enable_api_access: DF.Check
		enable_custom_reports: DF.Check
		enable_mobile_money_integration: DF.Check
		enable_multi_branch: DF.Check
		enable_sms_integration: DF.Check
		enable_white_label: DF.Check
		export_limit_per_month: DF.Int
		max_budget_items: DF.Int
		max_departments: DF.Int
		max_members: DF.Int
		max_reports_per_month: DF.Int
		mobile_money_monthly_cost: DF.Currency
		mobile_money_transaction_fee: DF.Percent
		monthly_cost: DF.Currency
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
		subscription_end_date: DF.Date
		subscription_package: DF.Literal["Starter", "Professional", "Premium", "Enterprise"]
		subscription_start_date: DF.Date
		subscription_status: DF.Literal["Active", "Expired", "Suspended", "Trial"]
		supported_providers: DF.Literal["M-Pesa Only", "M-Pesa + Tigo Pesa", "All Providers (M-Pesa, Tigo Pesa, Airtel Money, HaloPesa)"]
		tigo_pesa_api_key: DF.Password | None
		usage_report_frequency: DF.Literal["Weekly", "Monthly", "Quarterly"]
	# end: auto-generated types

	def validate(self):
		"""Validate StewardPro Settings"""
		self.validate_subscription_dates()
		self.validate_email_addresses()
		self.set_package_defaults()
		self.update_member_count()
		self.validate_feature_access()

	def validate_subscription_dates(self):
		"""Validate subscription start and end dates"""
		if self.subscription_start_date and self.subscription_end_date:
			if getdate(self.subscription_end_date) <= getdate(self.subscription_start_date):
				frappe.throw("Subscription end date must be after start date")

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

	def set_package_defaults(self):
		"""Set default values based on subscription package"""
		package_settings = self.get_package_settings()
		
		# Set costs
		self.monthly_cost = package_settings.get('monthly_cost', 0)
		self.annual_cost = package_settings.get('annual_cost', 0)
		
		# Set limits
		self.max_members = package_settings.get('max_members', 200)
		self.max_departments = package_settings.get('max_departments', 10)
		self.max_budget_items = package_settings.get('max_budget_items', 100)
		self.max_reports_per_month = package_settings.get('max_reports_per_month', 50)
		self.storage_limit_gb = package_settings.get('storage_limit_gb', 5)
		self.api_calls_per_month = package_settings.get('api_calls_per_month', 1000)
		self.export_limit_per_month = package_settings.get('export_limit_per_month', 20)
		self.data_retention_months = package_settings.get('data_retention_months', 24)
		
		# Set SMS settings
		if package_settings.get('sms_included'):
			self.enable_sms_integration = 1
			self.sms_monthly_quota = package_settings.get('sms_quota', 0)
		
		# Set mobile money settings
		if package_settings.get('mobile_money_included'):
			self.enable_mobile_money_integration = 1
			self.mobile_money_monthly_cost = package_settings.get('mobile_money_cost', 0)
		
		# Set advanced features
		advanced_features = package_settings.get('advanced_features', {})
		self.enable_advanced_analytics = advanced_features.get('analytics', 0)
		self.enable_multi_branch = advanced_features.get('multi_branch', 0)
		self.enable_api_access = advanced_features.get('api_access', 0)
		self.enable_custom_reports = advanced_features.get('custom_reports', 0)
		self.enable_white_label = advanced_features.get('white_label', 0)
		self.dedicated_support = advanced_features.get('dedicated_support', 0)
		self.priority_support = advanced_features.get('priority_support', 0)
		self.onsite_training = advanced_features.get('onsite_training', 0)

	def get_package_settings(self):
		"""Get settings for the current subscription package"""
		package_configs = {
			'Starter': {
				'monthly_cost': 3000000,  # TZS 3M
				'annual_cost': 32400000,  # 10% discount
				'max_members': 200,
				'max_departments': 10,
				'max_budget_items': 100,
				'max_reports_per_month': 50,
				'storage_limit_gb': 5,
				'api_calls_per_month': 1000,
				'export_limit_per_month': 20,
				'data_retention_months': 24,
				'sms_included': False,
				'mobile_money_included': False,
				'advanced_features': {
					'analytics': 0, 'multi_branch': 0, 'api_access': 0,
					'custom_reports': 0, 'white_label': 0, 'dedicated_support': 0,
					'priority_support': 0, 'onsite_training': 0
				}
			},
			'Professional': {
				'monthly_cost': 5500000,  # TZS 5.5M
				'annual_cost': 59400000,  # 10% discount
				'max_members': 1000,
				'max_departments': 25,
				'max_budget_items': 500,
				'max_reports_per_month': 100,
				'storage_limit_gb': 15,
				'api_calls_per_month': 5000,
				'export_limit_per_month': 50,
				'data_retention_months': 36,
				'sms_included': False,
				'mobile_money_included': False,
				'advanced_features': {
					'analytics': 1, 'multi_branch': 0, 'api_access': 0,
					'custom_reports': 1, 'white_label': 0, 'dedicated_support': 0,
					'priority_support': 1, 'onsite_training': 0
				}
			},
			'Premium': {
				'monthly_cost': 8500000,  # TZS 8.5M
				'annual_cost': 91800000,  # 10% discount
				'max_members': -1,  # Unlimited
				'max_departments': 50,
				'max_budget_items': 1000,
				'max_reports_per_month': 200,
				'storage_limit_gb': 50,
				'api_calls_per_month': 15000,
				'export_limit_per_month': 100,
				'data_retention_months': 60,
				'sms_included': True,
				'sms_quota': 500,
				'mobile_money_included': True,
				'mobile_money_cost': 0,  # Included in package
				'advanced_features': {
					'analytics': 1, 'multi_branch': 1, 'api_access': 1,
					'custom_reports': 1, 'white_label': 0, 'dedicated_support': 1,
					'priority_support': 1, 'onsite_training': 0
				}
			},
			'Enterprise': {
				'monthly_cost': 15000000,  # TZS 15M
				'annual_cost': 162000000,  # 10% discount
				'max_members': -1,  # Unlimited
				'max_departments': -1,  # Unlimited
				'max_budget_items': -1,  # Unlimited
				'max_reports_per_month': -1,  # Unlimited
				'storage_limit_gb': 200,
				'api_calls_per_month': 50000,
				'export_limit_per_month': -1,  # Unlimited
				'data_retention_months': 120,
				'sms_included': True,
				'sms_quota': 2000,
				'mobile_money_included': True,
				'mobile_money_cost': 0,  # Included in package
				'advanced_features': {
					'analytics': 1, 'multi_branch': 1, 'api_access': 1,
					'custom_reports': 1, 'white_label': 1, 'dedicated_support': 1,
					'priority_support': 1, 'onsite_training': 1
				}
			}
		}
		
		return package_configs.get(self.subscription_package, package_configs['Starter'])

	def update_member_count(self):
		"""Update current member count"""
		try:
			self.current_member_count = frappe.db.count('Member', {'status': "Active"})
		except:
			self.current_member_count = 0

	def validate_feature_access(self):
		"""Validate that enabled features are allowed for current package"""
		if self.subscription_status in ['Expired', 'Suspended']:
			# Disable all premium features for expired/suspended subscriptions
			self.enable_sms_integration = 0
			self.enable_mobile_money_integration = 0
			self.enable_advanced_analytics = 0
			self.enable_multi_branch = 0
			self.enable_api_access = 0
			self.enable_custom_reports = 0
			self.enable_white_label = 0
			return
		
		package_settings = self.get_package_settings()
		
		# Validate SMS integration
		if self.enable_sms_integration and not package_settings.get('sms_included'):
			if self.subscription_package in ['Starter', 'Professional']:
				frappe.msgprint(
					f"SMS Integration is not included in {self.subscription_package} package. "
					"Please upgrade to Premium or Enterprise, or purchase SMS add-on.",
					alert=True
				)
		
		# Validate mobile money integration
		if self.enable_mobile_money_integration and not package_settings.get('mobile_money_included'):
			if self.subscription_package in ['Starter', 'Professional']:
				frappe.msgprint(
					f"Mobile Money Integration is not included in {self.subscription_package} package. "
					"Please upgrade to Premium or Enterprise, or purchase Mobile Money add-on.",
					alert=True
				)

	def check_subscription_status(self):
		"""Check if subscription is active and update status if needed"""
		if self.subscription_end_date and getdate(self.subscription_end_date) < getdate(today()):
			self.subscription_status = 'Expired'
			self.save()
			return False
		return self.subscription_status == 'Active'

	def is_feature_enabled(self, feature):
		"""Check if a specific feature is enabled and subscription is active"""
		if not self.check_subscription_status():
			return False
		
		feature_map = {
			'sms': self.enable_sms_integration,
			'mobile_money': self.enable_mobile_money_integration,
			'advanced_analytics': self.enable_advanced_analytics,
			'multi_branch': self.enable_multi_branch,
			'api_access': self.enable_api_access,
			'custom_reports': self.enable_custom_reports,
			'white_label': self.enable_white_label
		}
		
		return feature_map.get(feature, False)

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
			'doctype': 'StewardPro Settings',
			'subscription_package': 'Starter',
			'subscription_status': 'Trial',
			'subscription_start_date': today(),
			'subscription_end_date': add_months(today(), 1)
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
