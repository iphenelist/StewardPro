# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

# Mapping from account_type to the canonical root group account name
ROOT_ACCOUNT_NAMES = {
	"Asset": "Church Assets",
	"Liability": "Church Liabilities",
	"Income": "Church Income",
	"Expense": "Church Expense",
}


def ensure_root_accounts():
	"""Create root group accounts (Income, Expense, Asset, Liability) if missing."""
	root_accounts = [
		{
			"account_name": "Church Assets",
			"account_type": "Asset",
			"is_group": 1,
			"description": "Root group for all church asset accounts",
		},
		{
			"account_name": "Church Liabilities",
			"account_type": "Liability",
			"is_group": 1,
			"description": "Root group for all church liability accounts",
		},
		{
			"account_name": "Church Income",
			"account_type": "Income",
			"is_group": 1,
			"description": "Root group for all church income accounts",
		},
		{
			"account_name": "Church Expense",
			"account_type": "Expense",
			"is_group": 1,
			"description": "Root group for all church expense accounts",
		},
	]
	for acct in root_accounts:
		if not frappe.db.exists("Church Account", {"account_name": acct["account_name"]}):
			doc = frappe.get_doc({"doctype": "Church Account", "enabled": 1, **acct})
			doc.insert(ignore_permissions=True)
	frappe.db.commit()


def get_root_account(account_type):
	"""Return the name of the root group account for the given account_type."""
	account_name = ROOT_ACCOUNT_NAMES.get(account_type)
	if not account_name:
		return None
	return frappe.db.get_value(
		"Church Account",
		{"account_name": account_name, "is_group": 1},
		"name",
	)


def create_department_accounts(department_name):
	"""
	Create Income, Expense, and Fund accounts for a church department.

	Each department gets:
	  - <Department> Income   (Income type, Offering subtype)
	  - <Department> Expense  (Expense type, Ministry Expense subtype)
	  - <Department> Fund     (Asset type, Fund subtype)

	Root group accounts are created automatically if they don't exist.
	"""
	ensure_root_accounts()

	income_root = get_root_account("Income")
	expense_root = get_root_account("Expense")
	asset_root = get_root_account("Asset")

	accounts = [
		{
			"account_name": f"{department_name} Income",
			"account_type": "Income",
			"account_subtype": "Offering",
			"parent_account": income_root,
			"is_group": 0,
			"description": f"Income account for {department_name} department",
		},
		{
			"account_name": f"{department_name} Expense",
			"account_type": "Expense",
			"account_subtype": "Ministry Expense",
			"parent_account": expense_root,
			"is_group": 0,
			"description": f"Expense account for {department_name} department",
		},
		{
			"account_name": f"{department_name} Fund",
			"account_type": "Asset",
			"account_subtype": "Fund",
			"parent_account": asset_root,
			"is_group": 0,
			"description": f"Fund/reserve account for {department_name} department",
		},
	]

	created = []
	for acct in accounts:
		if not frappe.db.exists("Church Account", {"account_name": acct["account_name"]}):
			doc = frappe.get_doc({"doctype": "Church Account", "enabled": 1, **acct})
			doc.insert(ignore_permissions=True)
			created.append(acct["account_name"])

	if created:
		frappe.db.commit()
		frappe.logger().info(
			f"Created accounts for department '{department_name}': {', '.join(created)}"
		)

	return created
