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




