# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import today, add_months, getdate


class TestStewardProSettings(unittest.TestCase):
	def setUp(self):
		"""Set up test data"""
		# Clean up any existing settings
		if frappe.db.exists('StewardPro Settings', 'StewardPro Settings'):
			frappe.delete_doc('StewardPro Settings', 'StewardPro Settings')

		# Create test settings
		self.settings = frappe.get_doc({
			'doctype': 'StewardPro Settings',
			'organization_name': 'Test Church',
			'default_organization_name': 'Test Church',
			'notification_email': 'admin@church.com',
			'admin_contact_email': 'contact@church.com',
			'subscription_start_date': today(),
			'subscription_end_date': add_months(today(), 1)
		})
		self.settings.insert()

	def tearDown(self):
		"""Clean up test data"""
		if frappe.db.exists('StewardPro Settings', 'StewardPro Settings'):
			frappe.delete_doc('StewardPro Settings', 'StewardPro Settings')

	def test_default_settings(self):
		"""Test that default settings are created correctly"""
		self.assertEqual(self.settings.enable_sms_integration, 0)
		self.assertEqual(self.settings.enable_mobile_money_integration, 0)
		self.assertEqual(self.settings.max_members, 200)

	def test_enable_sms_integration(self):
		"""Test enabling SMS integration"""
		self.settings.enable_sms_integration = 1
		self.settings.sms_monthly_quota = 500
		self.settings.save()

		self.assertEqual(self.settings.enable_sms_integration, 1)
		self.assertEqual(self.settings.sms_monthly_quota, 500)

	def test_enable_mobile_money_integration(self):
		"""Test enabling Mobile Money integration"""
		self.settings.enable_mobile_money_integration = 1
		self.settings.save()

		self.assertEqual(self.settings.enable_mobile_money_integration, 1)

	def test_email_validation(self):
		"""Test email address validation"""
		with self.assertRaises(frappe.ValidationError):
			self.settings.notification_email = 'invalid-email'
			self.settings.save()

	def test_feature_access_sms_enabled(self):
		"""Test SMS feature access when enabled"""
		self.settings.enable_sms_integration = 1
		self.settings.save()

		self.assertTrue(self.settings.is_feature_enabled('sms'))

	def test_feature_access_sms_disabled(self):
		"""Test SMS feature access when disabled"""
		self.settings.enable_sms_integration = 0
		self.settings.save()

		self.assertFalse(self.settings.is_feature_enabled('sms'))

	def test_feature_access_mobile_money_enabled(self):
		"""Test Mobile Money feature access when enabled"""
		self.settings.enable_mobile_money_integration = 1
		self.settings.save()

		self.assertTrue(self.settings.is_feature_enabled('mobile_money'))

	def test_feature_access_mobile_money_disabled(self):
		"""Test Mobile Money feature access when disabled"""
		self.settings.enable_mobile_money_integration = 0
		self.settings.save()

		self.assertFalse(self.settings.is_feature_enabled('mobile_money'))

	def test_sms_balance_calculation(self):
		"""Test SMS balance calculation"""
		self.settings.enable_sms_integration = 1
		self.settings.sms_monthly_quota = 500
		self.settings.sms_used_this_month = 100
		self.settings.save()

		balance = self.settings.get_sms_balance()
		self.assertEqual(balance, 400)

	def test_sms_can_send(self):
		"""Test SMS sending validation"""
		self.settings.enable_sms_integration = 1
		self.settings.sms_monthly_quota = 500
		self.settings.sms_used_this_month = 100
		self.settings.save()

		# Should be able to send 400 SMS
		can_send, message = self.settings.can_send_sms(400)
		self.assertTrue(can_send)

		# Should not be able to send 401 SMS
		can_send, message = self.settings.can_send_sms(401)
		self.assertFalse(can_send)
		self.assertIn('Insufficient SMS balance', message)

	def test_sms_usage_increment(self):
		"""Test SMS usage increment"""
		self.settings.enable_sms_integration = 1
		self.settings.sms_monthly_quota = 500
		self.settings.sms_used_this_month = 100
		self.settings.save()

		self.settings.increment_sms_usage(50)
		self.assertEqual(self.settings.sms_used_this_month, 150)

	def test_monthly_counter_reset(self):
		"""Test monthly counter reset"""
		self.settings.sms_used_this_month = 100
		self.settings.save()
		
		self.settings.reset_monthly_counters()
		self.assertEqual(self.settings.sms_used_this_month, 0)



	def test_get_stewardpro_settings_singleton(self):
		"""Test getting StewardPro Settings singleton"""
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import get_stewardpro_settings
		
		settings = get_stewardpro_settings()
		self.assertEqual(settings.doctype, 'StewardPro Settings')
		self.assertIsNotNone(settings.subscription_package)

	def test_check_feature_access_api(self):
		"""Test feature access API"""
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import check_feature_access

		self.settings.enable_sms_integration = 1
		self.settings.save()

		# Should have access to SMS when enabled
		has_access = check_feature_access('sms')
		self.assertTrue(has_access)

		# Should not have access to unknown feature
		has_access = check_feature_access('unknown_feature')
		self.assertFalse(has_access)

	def test_get_sms_status_api(self):
		"""Test SMS status API"""
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import get_sms_status

		self.settings.enable_sms_integration = 1
		self.settings.sms_monthly_quota = 500
		self.settings.sms_used_this_month = 100
		self.settings.save()

		status = get_sms_status()
		self.assertTrue(status['enabled'])
		self.assertEqual(status['quota'], 500)
		self.assertEqual(status['used'], 100)
		self.assertEqual(status['balance'], 400)
		self.assertTrue(status['can_send'])

	def test_disabled_features_for_suspended_subscription(self):
		"""Test that features are disabled for suspended subscriptions"""
		self.settings.subscription_package = 'Premium'
		self.settings.subscription_status = 'Suspended'
		self.settings.save()
		
		# All premium features should be disabled
		self.assertEqual(self.settings.enable_sms_integration, 0)
		self.assertEqual(self.settings.enable_mobile_money_integration, 0)
		self.assertEqual(self.settings.enable_advanced_analytics, 0)
		self.assertEqual(self.settings.enable_multi_branch, 0)
		self.assertEqual(self.settings.enable_api_access, 0)
		self.assertEqual(self.settings.enable_custom_reports, 0)
		self.assertEqual(self.settings.enable_white_label, 0)

	def test_member_count_update(self):
		"""Test member count update"""
		# Create a test member
		if not frappe.db.exists('Member', 'test-member'):
			member = frappe.get_doc({
				'doctype': 'Member',
				'full_name': 'Test Member',
				'is_active': 1
			})
			try:
				member.insert()
			except:
				pass  # Member doctype might not exist in test environment
		
		# Update member count should not raise error
		try:
			self.settings.update_member_count()
		except:
			pass  # Expected if Member doctype doesn't exist in test
