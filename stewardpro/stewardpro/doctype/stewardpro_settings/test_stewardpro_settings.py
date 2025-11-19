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
			'doctype': 'StewardPro Settings'
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

	def test_enable_sms_integration(self):
		"""Test enabling SMS integration"""
		self.settings.enable_sms_integration = 1
		self.settings.save()

		self.assertEqual(self.settings.enable_sms_integration, 1)

	def test_enable_mobile_money_integration(self):
		"""Test enabling Mobile Money integration"""
		self.settings.enable_mobile_money_integration = 1
		self.settings.save()

		self.assertEqual(self.settings.enable_mobile_money_integration, 1)

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





	def test_get_stewardpro_settings_singleton(self):
		"""Test getting StewardPro Settings singleton"""
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import get_stewardpro_settings

		settings = get_stewardpro_settings()
		self.assertEqual(settings.doctype, 'StewardPro Settings')

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

	def test_sms_configuration_fields(self):
		"""Test SMS configuration fields"""
		self.settings.enable_sms_integration = 1
		self.settings.sms_api_key = "test_key_123"
		self.settings.sms_api_secret = "test_secret_456"
		self.settings.sms_sender_id = "TestSender"
		self.settings.sms_base_url = "https://api.example.com/sms/send"
		self.settings.save()

		# Verify all fields are saved
		self.assertEqual(self.settings.sms_api_key, "test_key_123")
		self.assertEqual(self.settings.sms_api_secret, "test_secret_456")
		self.assertEqual(self.settings.sms_sender_id, "TestSender")
		self.assertEqual(self.settings.sms_base_url, "https://api.example.com/sms/send")

	def test_get_sms_settings_when_enabled(self):
		"""Test get_sms_settings function when SMS is enabled"""
		from stewardpro.stewardpro.api.sms import get_sms_settings

		self.settings.enable_sms_integration = 1
		self.settings.sms_api_key = "test_key"
		self.settings.sms_api_secret = "test_secret"
		self.settings.sms_sender_id = "TestSender"
		self.settings.sms_base_url = "https://api.example.com/sms"
		self.settings.save()

		# Should return settings without error
		settings = get_sms_settings()
		self.assertIsNotNone(settings)
		self.assertEqual(settings.enable_sms_integration, 1)

	def test_get_sms_settings_when_disabled(self):
		"""Test get_sms_settings function when SMS is disabled"""
		from stewardpro.stewardpro.api.sms import get_sms_settings

		self.settings.enable_sms_integration = 0
		self.settings.save()

		# Should raise exception when SMS is disabled
		with self.assertRaises(Exception):
			get_sms_settings()

	def test_mobile_money_configuration_fields(self):
		"""Test Mobile Money configuration fields"""
		self.settings.enable_mobile_money_integration = 1
		self.settings.money_api_key = "test_api_key_123"
		self.settings.money_public_key = "test_public_key_456"
		self.settings.mobile_money_base_url = "https://api.example.com/payment"
		self.settings.save()

		# Verify all fields are saved
		self.assertEqual(self.settings.money_api_key, "test_api_key_123")
		self.assertEqual(self.settings.money_public_key, "test_public_key_456")
		self.assertEqual(self.settings.mobile_money_base_url, "https://api.example.com/payment")

	def test_get_mobile_money_settings_when_enabled(self):
		"""Test get_mobile_money_settings function when Mobile Money is enabled"""
		from stewardpro.stewardpro.api.money import get_mobile_money_settings

		self.settings.enable_mobile_money_integration = 1
		self.settings.money_api_key = "test_key"
		self.settings.money_public_key = "test_public"
		self.settings.mobile_money_base_url = "https://api.example.com/payment"
		self.settings.save()

		# Should return settings without error
		settings = get_mobile_money_settings()
		self.assertIsNotNone(settings)
		self.assertEqual(settings.enable_mobile_money_integration, 1)

	def test_get_mobile_money_settings_when_disabled(self):
		"""Test get_mobile_money_settings function when Mobile Money is disabled"""
		from stewardpro.stewardpro.api.money import get_mobile_money_settings

		self.settings.enable_mobile_money_integration = 0
		self.settings.save()

		# Should raise exception when Mobile Money is disabled
		with self.assertRaises(Exception):
			get_mobile_money_settings()
