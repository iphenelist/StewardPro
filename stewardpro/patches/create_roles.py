# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""Create or update church-specific roles"""
	create_church_roles()
	setup_permissions()


def create_church_roles():
	"""Create church-specific roles"""
	roles = [
		{
			"role_name": "Department Head",
			"desk_access": 1,
			"description": "Department head with access to all department-related transactions and reports"
		},
		{
			"role_name": "Treasurer",
			"desk_access": 1,
			"description": "Church treasurer with access to all financial transactions and reports"
		},
		{
			"role_name": "Elder",
			"desk_access": 1,
			"description": "Church elder with full access to all features and reports"
		}
	]
	
	for role_data in roles:
		if not frappe.db.exists("Role", role_data["role_name"]):
			role = frappe.get_doc({
				"doctype": "Role",
				"role_name": role_data["role_name"],
				"desk_access": role_data["desk_access"]
			})
			role.insert(ignore_permissions=True)
			frappe.db.commit()
			print(f"✅ Created role: {role_data['role_name']}")
		else:
			print(f"ℹ️  Role already exists: {role_data['role_name']}")


def setup_permissions():
	"""Setup permissions for church management doctypes"""
	from frappe.permissions import add_permission, update_permission_property

	# Member permissions
	if frappe.db.exists("DocType", "Member"):
		setup_member_permissions(add_permission, update_permission_property)

	# Tithes and Offerings permissions
	if frappe.db.exists("DocType", "Tithes and Offerings"):
		setup_tithes_offerings_permissions(add_permission, update_permission_property)

	# Church Expense permissions
	if frappe.db.exists("DocType", "Church Expense"):
		setup_church_expense_permissions(add_permission, update_permission_property)

	# Department Budget permissions
	if frappe.db.exists("DocType", "Department Budget"):
		setup_department_budget_permissions(add_permission, update_permission_property)


def setup_member_permissions(add_permission, update_permission_property):
	"""Setup permissions for Member doctype"""
	doctype = "Member"
	# System Manager - Full access
	add_permission(doctype, "System Manager", 0)
	for ptype in ["read", "write", "create", "delete", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "System Manager", 0, ptype, 1)
	# Treasurer - Full access except delete
	add_permission(doctype, "Treasurer", 0)
	for ptype in ["read", "write", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Treasurer", 0, ptype, 1)
	
	# Department Head - Read, write, create access
	add_permission(doctype, "Department Head", 0)
	for ptype in ["read", "write", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Department Head", 0, ptype, 1)
	
	# Elder - Full access
	add_permission(doctype, "Elder", 0)
	for ptype in ["read", "write", "create", "delete", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Elder", 0, ptype, 1)


def setup_tithes_offerings_permissions(add_permission, update_permission_property):
	"""Setup permissions for Tithes and Offerings doctype"""
	doctype = "Tithes and Offerings"
	# System Manager - Full access
	add_permission(doctype, "System Manager", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "System Manager", 0, ptype, 1)	# Treasurer - Full access
	add_permission(doctype, "Treasurer", 0)
	for ptype in ["read", "write", "create", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Treasurer", 0, ptype, 1)
	
	# Department Head - Read and create access
	add_permission(doctype, "Department Head", 0)
	for ptype in ["read", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Department Head", 0, ptype, 1)
	
	# Elder - Full access
	add_permission(doctype, "Elder", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Elder", 0, ptype, 1)


def setup_church_expense_permissions(add_permission, update_permission_property):
	"""Setup permissions for Church Expense doctype"""
	doctype = "Church Expense"
	# System Manager - Full access
	add_permission(doctype, "System Manager", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "System Manager", 0, ptype, 1)
	# Treasurer - Full access
	add_permission(doctype, "Treasurer", 0)
	for ptype in ["read", "write", "create", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Treasurer", 0, ptype, 1)
	
	# Department Head - Read and create access
	add_permission(doctype, "Department Head", 0)
	for ptype in ["read", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Department Head", 0, ptype, 1)
	
	# Elder - Full access
	add_permission(doctype, "Elder", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Elder", 0, ptype, 1)


def setup_department_budget_permissions(add_permission, update_permission_property):
	"""Setup permissions for Department Budget doctype"""
	doctype = "Department Budget"
	# System Manager - Full access
	add_permission(doctype, "System Manager", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "System Manager", 0, ptype, 1)
	# Treasurer - Full access
	add_permission(doctype, "Treasurer", 0)
	for ptype in ["read", "write", "create", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Treasurer", 0, ptype, 1)
	
	# Department Head - Full access to department budgets
	add_permission(doctype, "Department Head", 0)
	for ptype in ["read", "write", "create", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Department Head", 0, ptype, 1)
	
	# Elder - Full access
	add_permission(doctype, "Elder", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Elder", 0, ptype, 1)
