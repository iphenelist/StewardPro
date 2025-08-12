# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
import unittest
from frappe.utils import nowdate, getdate


class TestDepartment(unittest.TestCase):
	def setUp(self):
		"""Set up test data"""
		# Clean up any existing test departments
		frappe.db.delete("Department", {"department_name": ["like", "Test%"]})
		frappe.db.commit()
		
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.delete("Department", {"department_name": ["like", "Test%"]})
		frappe.db.commit()
		
	def test_create_department(self):
		"""Test creating a new department"""
		dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Youth Ministry",
			"department_code": "YTH",
			"description": "Youth ministry department for testing",
			"annual_budget": 5000.00,
			"is_active": 1
		})
		dept.insert()
		
		self.assertEqual(dept.department_name, "Test Youth Ministry")
		self.assertEqual(dept.department_code, "YTH")
		self.assertTrue(dept.is_active)
		
	def test_department_code_uppercase(self):
		"""Test that department code is automatically converted to uppercase"""
		dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Music Ministry",
			"department_code": "mus",
			"is_active": 1
		})
		dept.insert()
		
		self.assertEqual(dept.department_code, "MUS")
		
	def test_parent_department_validation(self):
		"""Test that department cannot be its own parent"""
		dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Admin",
			"department_code": "ADM",
			"is_active": 1
		})
		dept.insert()
		
		# Try to set itself as parent
		dept.parent_department = dept.name
		
		with self.assertRaises(frappe.ValidationError):
			dept.save()
			
	def test_budget_year_default(self):
		"""Test that budget year defaults to current year"""
		dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Finance",
			"department_code": "FIN",
			"is_active": 1
		})
		dept.insert()
		
		current_year = getdate(nowdate()).year
		self.assertEqual(dept.budget_year, current_year)
		
	def test_department_hierarchy(self):
		"""Test department hierarchy functionality"""
		# Create parent department
		parent_dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Ministries",
			"department_code": "MIN",
			"is_active": 1
		})
		parent_dept.insert()
		
		# Create child department
		child_dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Children Ministry",
			"department_code": "CHI",
			"parent_department": parent_dept.name,
			"is_active": 1
		})
		child_dept.insert()
		
		# Test hierarchy path
		hierarchy = child_dept.get_department_hierarchy()
		self.assertEqual(hierarchy, "Test Ministries > Test Children Ministry")
		
		# Test child departments
		children = parent_dept.get_child_departments()
		self.assertEqual(len(children), 1)
		self.assertEqual(children[0].name, child_dept.name)
		
	def test_budget_calculation(self):
		"""Test budget calculation including child departments"""
		# Create parent department with budget
		parent_dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Operations",
			"department_code": "OPS",
			"annual_budget": 10000.00,
			"is_active": 1
		})
		parent_dept.insert()
		
		# Create child department with budget
		child_dept = frappe.get_doc({
			"doctype": "Department",
			"department_name": "Test Maintenance",
			"department_code": "MNT",
			"parent_department": parent_dept.name,
			"annual_budget": 3000.00,
			"is_active": 1
		})
		child_dept.insert()
		
		# Test total budget calculation
		total_budget = parent_dept.get_total_budget_allocated()
		self.assertEqual(total_budget, 13000.00)  # 10000 + 3000
