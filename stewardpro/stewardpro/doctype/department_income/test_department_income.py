# Copyright (c) 2025, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.test_runner import make_test_records
from frappe.tests.utils import FrappeTestCase


class TestDepartmentIncome(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create a test department if it doesn't exist
		if not frappe.db.exists("Department", "Test Department"):
			frappe.get_doc({
				"doctype": "Department",
				"department_name": "Test Department",
				"department_code": "TEST",
				"is_active": 1
			}).insert()

	def test_create_department_income(self):
		"""Test creating a department income record"""
		doc = frappe.get_doc({
			"doctype": "Department Income",
			"date": frappe.utils.today(),
			"department": "Test Department",
			"income_type": "Tithe",
			"amount": 1000,
			"payment_mode": "Cash",
			"description": "Test income"
		})
		doc.insert()
		self.assertTrue(doc.name)

	def test_validate_amount(self):
		"""Test that amount must be positive"""
		doc = frappe.get_doc({
			"doctype": "Department Income",
			"date": frappe.utils.today(),
			"department": "Test Department",
			"income_type": "Offering",
			"amount": -100,
			"payment_mode": "Cash"
		})
		self.assertRaises(frappe.ValidationError, doc.insert)

	def test_validate_department_exists(self):
		"""Test that department must exist"""
		doc = frappe.get_doc({
			"doctype": "Department Income",
			"date": frappe.utils.today(),
			"department": "Non Existent Department",
			"income_type": "Donation",
			"amount": 500,
			"payment_mode": "Bank Transfer"
		})
		self.assertRaises(frappe.DoesNotExistError, doc.insert)

