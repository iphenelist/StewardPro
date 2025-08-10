# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.permissions import add_permission, update_permission_property


def after_install():
	"""Setup church management after app installation"""
	create_church_roles()
	setup_permissions()
	create_default_fiscal_year()


def create_church_roles():
	"""Create church-specific roles"""
	roles = [
		{
			"role_name": "Treasurer",
			"desk_access": 1,
			"description": "Church treasurer with financial management access"
		},
		{
			"role_name": "Church Member",
			"desk_access": 1,
			"description": "Regular church member with limited access"
		},
		{
			"role_name": "Church Elder",
			"desk_access": 1,
			"description": "Church elder with administrative access"
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


def setup_permissions():
	"""Setup permissions for church management doctypes"""
	
	# Church Member permissions
	setup_church_member_permissions()
	
	# Tithes and Offerings permissions
	setup_tithes_offerings_permissions()
	
	# Church Expense permissions
	setup_church_expense_permissions()
	
	# Department Budget permissions
	setup_department_budget_permissions()
	
	# Remittance permissions
	setup_remittance_permissions()


def setup_church_member_permissions():
	"""Setup permissions for Church Member doctype"""
	doctype = "Church Member"
	
	# System Manager - Full access
	add_permission(doctype, "System Manager", 0)
	for ptype in ["read", "write", "create", "delete", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "System Manager", 0, ptype, 1)
	
	# Treasurer - Full access except delete
	add_permission(doctype, "Treasurer", 0)
	for ptype in ["read", "write", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Treasurer", 0, ptype, 1)
	
	# Church Elder - Read, write, create access
	add_permission(doctype, "Church Elder", 0)
	for ptype in ["read", "write", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Elder", 0, ptype, 1)
	
	# Church Member - Read only access
	add_permission(doctype, "Church Member", 0)
	for ptype in ["read", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Member", 0, ptype, 1)


def setup_tithes_offerings_permissions():
	"""Setup permissions for Tithes and Offerings doctype"""
	doctype = "Tithes and Offerings"
	
	# System Manager - Full access
	add_permission(doctype, "System Manager", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "System Manager", 0, ptype, 1)
	
	# Treasurer - Full access
	add_permission(doctype, "Treasurer", 0)
	for ptype in ["read", "write", "create", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Treasurer", 0, ptype, 1)
	
	# Church Elder - Read and create access
	add_permission(doctype, "Church Elder", 0)
	for ptype in ["read", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Elder", 0, ptype, 1)
	
	# Church Member - Read only access
	add_permission(doctype, "Church Member", 0)
	for ptype in ["read", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Member", 0, ptype, 1)


def setup_church_expense_permissions():
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
	
	# Church Elder - Read and create access
	add_permission(doctype, "Church Elder", 0)
	for ptype in ["read", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Elder", 0, ptype, 1)
	
	# Church Member - Read only access
	add_permission(doctype, "Church Member", 0)
	for ptype in ["read", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Member", 0, ptype, 1)


def setup_department_budget_permissions():
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
	
	# Church Elder - Read and create access
	add_permission(doctype, "Church Elder", 0)
	for ptype in ["read", "create", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Elder", 0, ptype, 1)
	
	# Church Member - Read only access
	add_permission(doctype, "Church Member", 0)
	for ptype in ["read", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Member", 0, ptype, 1)


def setup_remittance_permissions():
	"""Setup permissions for Remittance doctype"""
	doctype = "Remittance"
	
	# System Manager - Full access
	add_permission(doctype, "System Manager", 0)
	for ptype in ["read", "write", "create", "delete", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "System Manager", 0, ptype, 1)
	
	# Treasurer - Full access
	add_permission(doctype, "Treasurer", 0)
	for ptype in ["read", "write", "create", "submit", "cancel", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Treasurer", 0, ptype, 1)
	
	# Church Elder - Read only access
	add_permission(doctype, "Church Elder", 0)
	for ptype in ["read", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Elder", 0, ptype, 1)
	
	# Church Member - Read only access
	add_permission(doctype, "Church Member", 0)
	for ptype in ["read", "print", "email", "export", "report", "share"]:
		update_permission_property(doctype, "Church Member", 0, ptype, 1)


def create_default_fiscal_year():
	"""Create default fiscal year if it doesn't exist"""
	from datetime import datetime
	
	current_year = datetime.now().year
	fiscal_year_name = str(current_year)
	
	if not frappe.db.exists("Fiscal Year", fiscal_year_name):
		fiscal_year = frappe.get_doc({
			"doctype": "Fiscal Year",
			"year": fiscal_year_name,
			"year_start_date": f"{current_year}-01-01",
			"year_end_date": f"{current_year}-12-31"
		})
		fiscal_year.insert(ignore_permissions=True)
		frappe.db.commit()
