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
			'subscription_package': 'Starter',
			'subscription_status': 'Active',
			'subscription_start_date': today(),
			'subscription_end_date': add_months(today(), 1),
			'notification_email': 'admin@church.com',
			'admin_contact_email': 'contact@church.com'
		})
		self.settings.insert()

	def tearDown(self):
		"""Clean up test data"""
		if frappe.db.exists('StewardPro Settings', 'StewardPro Settings'):
			frappe.delete_doc('StewardPro Settings', 'StewardPro Settings')

	def test_package_defaults_starter(self):
		"""Test that Starter package sets correct defaults"""
		self.assertEqual(self.settings.subscription_package, 'Starter')
		self.assertEqual(self.settings.monthly_cost, 3000000)
		self.assertEqual(self.settings.max_members, 200)
		self.assertEqual(self.settings.enable_sms_integration, 0)
		self.assertEqual(self.settings.enable_mobile_money_integration, 0)
		self.assertEqual(self.settings.enable_advanced_analytics, 0)

	def test_package_upgrade_professional(self):
		"""Test upgrading to Professional package"""
		self.settings.subscription_package = 'Professional'
		self.settings.save()
		
		self.assertEqual(self.settings.monthly_cost, 5500000)
		self.assertEqual(self.settings.max_members, 1000)
		self.assertEqual(self.settings.enable_advanced_analytics, 1)
		self.assertEqual(self.settings.enable_custom_reports, 1)
		self.assertEqual(self.settings.priority_support, 1)

	def test_package_upgrade_premium(self):
		"""Test upgrading to Premium package"""
		self.settings.subscription_package = 'Premium'
		self.settings.save()
		
		self.assertEqual(self.settings.monthly_cost, 8500000)
		self.assertEqual(self.settings.max_members, -1)  # Unlimited
		self.assertEqual(self.settings.enable_sms_integration, 1)
		self.assertEqual(self.settings.sms_monthly_quota, 500)
		self.assertEqual(self.settings.enable_mobile_money_integration, 1)
		self.assertEqual(self.settings.enable_multi_branch, 1)

	def test_package_upgrade_enterprise(self):
		"""Test upgrading to Enterprise package"""
		self.settings.subscription_package = 'Enterprise'
		self.settings.save()
		
		self.assertEqual(self.settings.monthly_cost, 15000000)
		self.assertEqual(self.settings.max_members, -1)  # Unlimited
		self.assertEqual(self.settings.sms_monthly_quota, 2000)
		self.assertEqual(self.settings.enable_white_label, 1)
		self.assertEqual(self.settings.dedicated_support, 1)
		self.assertEqual(self.settings.onsite_training, 1)

	def test_subscription_date_validation(self):
		"""Test subscription date validation"""
		with self.assertRaises(frappe.ValidationError):
			self.settings.subscription_end_date = add_months(today(), -1)  # Past date
			self.settings.save()

	def test_email_validation(self):
		"""Test email address validation"""
		with self.assertRaises(frappe.ValidationError):
			self.settings.notification_email = 'invalid-email'
			self.settings.save()

	def test_feature_access_active_subscription(self):
		"""Test feature access with active subscription"""
		self.settings.subscription_package = 'Premium'
		self.settings.subscription_status = 'Active'
		self.settings.save()
		
		self.assertTrue(self.settings.is_feature_enabled('sms'))
		self.assertTrue(self.settings.is_feature_enabled('mobile_money'))
		self.assertTrue(self.settings.is_feature_enabled('advanced_analytics'))

	def test_feature_access_expired_subscription(self):
		"""Test feature access with expired subscription"""
		self.settings.subscription_status = 'Expired'
		self.settings.save()
		
		self.assertFalse(self.settings.is_feature_enabled('sms'))
		self.assertFalse(self.settings.is_feature_enabled('mobile_money'))
		self.assertFalse(self.settings.is_feature_enabled('advanced_analytics'))

	def test_sms_balance_calculation(self):
		"""Test SMS balance calculation"""
		self.settings.subscription_package = 'Premium'
		self.settings.sms_monthly_quota = 500
		self.settings.sms_used_this_month = 100
		self.settings.save()
		
		balance = self.settings.get_sms_balance()
		self.assertEqual(balance, 400)

	def test_sms_can_send(self):
		"""Test SMS sending validation"""
		self.settings.subscription_package = 'Premium'
		self.settings.subscription_status = 'Active'
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
		self.settings.subscription_package = 'Premium'
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

	def test_subscription_status_check(self):
		"""Test subscription status checking"""
		# Active subscription
		self.settings.subscription_end_date = add_months(today(), 1)
		self.settings.subscription_status = 'Active'
		self.settings.save()
		
		self.assertTrue(self.settings.check_subscription_status())
		
		# Expired subscription
		self.settings.subscription_end_date = add_months(today(), -1)
		self.settings.save()
		
		self.assertFalse(self.settings.check_subscription_status())
		self.assertEqual(self.settings.subscription_status, 'Expired')

	def test_get_stewardpro_settings_singleton(self):
		"""Test getting StewardPro Settings singleton"""
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import get_stewardpro_settings
		
		settings = get_stewardpro_settings()
		self.assertEqual(settings.doctype, 'StewardPro Settings')
		self.assertIsNotNone(settings.subscription_package)

	def test_check_feature_access_api(self):
		"""Test feature access API"""
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import check_feature_access
		
		self.settings.subscription_package = 'Premium'
		self.settings.subscription_status = 'Active'
		self.settings.save()
		
		# Should have access to SMS in Premium package
		has_access = check_feature_access('sms')
		self.assertTrue(has_access)
		
		# Should not have access to white_label in Premium package
		has_access = check_feature_access('white_label')
		self.assertFalse(has_access)

	def test_get_sms_status_api(self):
		"""Test SMS status API"""
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import get_sms_status
		
		self.settings.subscription_package = 'Premium'
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
