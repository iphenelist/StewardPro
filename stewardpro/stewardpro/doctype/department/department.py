# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate


class Department(Document):
	def validate(self):
		"""Validate department data before saving"""
		self.validate_department_code()
		self.validate_parent_department()
		self.validate_budget_year()
		
	def validate_department_code(self):
		"""Ensure department code is uppercase and unique"""
		if self.department_code:
			self.department_code = self.department_code.upper()
			
	def validate_parent_department(self):
		"""Ensure department cannot be its own parent"""
		if self.parent_department and self.parent_department == self.name:
			frappe.throw("Department cannot be its own parent")
			
	def validate_budget_year(self):
		"""Set default budget year if not provided"""
		if not self.budget_year:
			self.budget_year = getdate(nowdate()).year
			
	def get_child_departments(self):
		"""Get all child departments"""
		return frappe.get_all(
			"Department",
			filters={"parent_department": self.name, "is_active": 1},
			fields=["name", "department_name", "department_code"]
		)
		
	def get_department_hierarchy(self):
		"""Get the full hierarchy path for this department"""
		hierarchy = [self.department_name]
		current_dept = self
		
		while current_dept.parent_department:
			parent = frappe.get_doc("Department", current_dept.parent_department)
			hierarchy.insert(0, parent.department_name)
			current_dept = parent
			
		return " > ".join(hierarchy)
		
	def get_total_budget_allocated(self):
		"""Get total budget allocated including child departments"""
		total_budget = self.annual_budget or 0
		
		# Add budgets from child departments
		child_departments = self.get_child_departments()
		for child in child_departments:
			child_doc = frappe.get_doc("Department", child.name)
			total_budget += child_doc.annual_budget or 0
			
		return total_budget
		
	@frappe.whitelist()
	def get_department_expenses(self, from_date=None, to_date=None):
		"""Get expenses for this department within date range"""
		filters = {
			"department": self.name,
			"docstatus": 1
		}
		
		if from_date:
			filters["expense_date"] = [">=", from_date]
		if to_date:
			filters["expense_date"] = ["<=", to_date]
			
		expenses = frappe.get_all(
			"Expense",
			filters=filters,
			fields=["name", "expense_date", "amount", "description", "expense_type"]
		)
		
		return expenses
		
	@frappe.whitelist()
	def get_budget_utilization(self, year=None):
		"""Get budget utilization for the department"""
		if not year:
			year = getdate(nowdate()).year

		# Get total expenses for the year
		expenses = frappe.db.sql("""
			SELECT SUM(amount) as total_expenses
			FROM `Department Expense`
			WHERE department = %s
			AND YEAR(expense_date) = %s
			AND docstatus = 1
		""", (self.name, year), as_dict=True)

		total_expenses = expenses[0].total_expenses or 0
		budget = self.annual_budget or 0

		utilization_percentage = (total_expenses / budget * 100) if budget > 0 else 0

		return {
			"budget": budget,
			"expenses": total_expenses,
			"remaining": budget - total_expenses,
			"utilization_percentage": utilization_percentage
		}

	@frappe.whitelist()
	def get_department_income(self, from_date=None, to_date=None):
		"""Get total income for this department within date range"""
		filters = {
			"department": self.name,
			"docstatus": 1
		}

		if from_date:
			filters["date"] = [">=", from_date]
		if to_date:
			filters["date"] = ["<=", to_date]

		income_records = frappe.get_all(
			"Department Income",
			filters=filters,
			fields=["name", "date", "amount", "income_type", "description"]
		)

		return income_records

	@frappe.whitelist()
	def get_total_income(self, year=None):
		"""Get total income for the department in a specific year"""
		if not year:
			year = getdate(nowdate()).year

		income = frappe.db.sql("""
			SELECT SUM(amount) as total_income
			FROM `tabDepartment Income`
			WHERE department = %s
			AND YEAR(date) = %s
			AND docstatus = 1
		""", (self.name, year), as_dict=True)

		return income[0].total_income or 0 if income else 0

	@frappe.whitelist()
	def get_income_by_type(self, year=None):
		"""Get income breakdown by type for the department"""
		if not year:
			year = getdate(nowdate()).year

		income_by_type = frappe.db.sql("""
			SELECT income_type, SUM(amount) as total
			FROM `tabDepartment Income`
			WHERE department = %s
			AND YEAR(date) = %s
			AND docstatus = 1
			GROUP BY income_type
		""", (self.name, year), as_dict=True)

		return income_by_type

	@frappe.whitelist()
	def get_department_balance(self, year=None):
		"""Get department balance (income - expenses) for the year"""
		if not year:
			year = getdate(nowdate()).year

		total_income = self.get_total_income(year)

		# Get total expenses for the year
		expenses = frappe.db.sql("""
			SELECT SUM(total_amount) as total_expenses
			FROM `tabDepartment Expense`
			WHERE department = %s
			AND YEAR(expense_date) = %s
			AND docstatus = 1
		""", (self.name, year), as_dict=True)

		total_expenses = expenses[0].total_expenses or 0 if expenses else 0
		balance = total_income - total_expenses

		return {
			"income": total_income,
			"expenses": total_expenses,
			"balance": balance
		}


@frappe.whitelist()
def get_department_tree():
	"""Get department hierarchy as tree structure"""
	departments = frappe.get_all(
		"Department",
		filters={"is_active": 1},
		fields=["name", "department_name", "parent_department", "department_code"],
		order_by="department_name"
	)
	
	# Build tree structure
	tree = []
	dept_map = {}
	
	# Create department map
	for dept in departments:
		dept_map[dept.name] = {
			"name": dept.name,
			"department_name": dept.department_name,
			"department_code": dept.department_code,
			"parent_department": dept.parent_department,
			"children": []
		}
	
	# Build hierarchy
	for dept in departments:
		if dept.parent_department and dept.parent_department in dept_map:
			dept_map[dept.parent_department]["children"].append(dept_map[dept.name])
		else:
			tree.append(dept_map[dept.name])
	
	return tree


@frappe.whitelist()
def get_active_departments():
	"""Get all active departments for dropdown/selection"""
	return frappe.get_all(
		"Department",
		filters={"is_active": 1},
		fields=["name", "department_name", "department_code"],
		order_by="department_name"
	)
