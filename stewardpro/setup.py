import frappe


def after_install():
	create_roles()
	create_default_departments()
	create_default_accounts()
	create_church_expense_workflow()


def create_roles():
	roles = [
		"Pastor",
		"Church Elder",
		"Church Clerk",
		"Treasurer",
		"SS Superintendent",
		"SS Teacher",
		"Deacon",
		"Church Member",
	]
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)


def create_default_departments():
	departments = [
		{"department_name": "Adventist Youth", "abbreviation": "AY", "department_type": "Ministry"},
		{"department_name": "Dorcas / Community Services", "abbreviation": "ACS", "department_type": "Service"},
		{"department_name": "Personal Ministries", "abbreviation": "PM", "department_type": "Ministry"},
		{"department_name": "Health Ministries", "abbreviation": "HM", "department_type": "Ministry"},
		{"department_name": "Music Ministry", "abbreviation": "MM", "department_type": "Ministry"},
		{"department_name": "Sabbath School", "abbreviation": "SS", "department_type": "Ministry"},
		{"department_name": "Deacons Ministry", "abbreviation": "DM", "department_type": "Service"},
		{"department_name": "Deaconesses Ministry", "abbreviation": "DSM", "department_type": "Service"},
		{"department_name": "Children's Ministries", "abbreviation": "CM", "department_type": "Ministry"},
		{"department_name": "Family Ministries", "abbreviation": "FM", "department_type": "Ministry"},
		{"department_name": "Communication", "abbreviation": "COM", "department_type": "Support"},
		{"department_name": "Education", "abbreviation": "EDU", "department_type": "Ministry"},
		{"department_name": "Stewardship", "abbreviation": "STW", "department_type": "Ministry"},
		{"department_name": "Women's Ministries", "abbreviation": "WM", "department_type": "Ministry"},
		{"department_name": "Men's Ministries", "abbreviation": "MEN", "department_type": "Ministry"},
		{"department_name": "Prayer Ministries", "abbreviation": "PRM", "department_type": "Ministry"},
		{"department_name": "Publishing Ministries", "abbreviation": "PUB", "department_type": "Ministry"},
	]
	for dept in departments:
		if not frappe.db.exists("Church Department", {"department_name": dept["department_name"]}):
			doc = frappe.get_doc({"doctype": "Church Department", "enabled": 1, **dept})
			doc.insert(ignore_permissions=True)


def create_default_accounts():
	"""Create root accounts and per-department accounts for all default departments."""
	from stewardpro.church_finance.utils import (
		create_department_accounts,
		ensure_root_accounts,
		sync_department_account_tags,
	)

	# 1. Create root group accounts first
	ensure_root_accounts()

	# 2. Create general church-wide accounts (non-department)
	from stewardpro.church_finance.utils import get_root_account

	income_root = get_root_account("Income")
	expense_root = get_root_account("Expense")
	asset_root = get_root_account("Asset")
	liability_root = get_root_account("Liability")

	general_accounts = [
		# Income accounts
		{
			"account_name": "Tithe Income",
			"account_type": "Income",
			"account_subtype": "Tithe",
			"parent_account": income_root,
			"is_group": 0,
			"description": "All tithe receipts from members",
		},
		{
			"account_name": "Regular Offering Income",
			"account_type": "Income",
			"account_subtype": "Offering",
			"parent_account": income_root,
			"is_group": 0,
			"description": "Regular offering receipts (local share)",
		},
		{
			"account_name": "Building Fund Income",
			"account_type": "Income",
			"account_subtype": "Fund",
			"parent_account": income_root,
			"is_group": 0,
			"description": "Church building fund contributions",
		},
		{
			"account_name": "Camp Meeting Income",
			"account_type": "Income",
			"account_subtype": "Offering",
			"parent_account": income_root,
			"is_group": 0,
			"description": "Camp meeting offering receipts",
		},
		# Expense accounts
		{
			"account_name": "General Administration Expense",
			"account_type": "Expense",
			"account_subtype": "Operating Expense",
			"parent_account": expense_root,
			"is_group": 0,
			"description": "General church administration expenses",
		},
		{
			"account_name": "Conference Remittance Expense",
			"account_type": "Expense",
			"account_subtype": "Operating Expense",
			"parent_account": expense_root,
			"is_group": 0,
			"description": "Tithe and offerings remitted to conference",
		},
		# Asset accounts
		{
			"account_name": "Church Cash",
			"account_type": "Asset",
			"account_subtype": "Cash",
			"parent_account": asset_root,
			"is_group": 0,
			"description": "Cash on hand",
		},
		{
			"account_name": "Church Bank Account",
			"account_type": "Asset",
			"account_subtype": "Bank",
			"parent_account": asset_root,
			"is_group": 0,
			"description": "Church bank account balance",
		},
		{
			"account_name": "Church Property",
			"account_type": "Asset",
			"account_subtype": "Property",
			"parent_account": asset_root,
			"is_group": 0,
			"description": "Church property and buildings",
		},
		# Liability accounts
		{
			"account_name": "Accounts Payable",
			"account_type": "Liability",
			"account_subtype": "Payable",
			"parent_account": liability_root,
			"is_group": 0,
			"description": "Amounts owed by the church",
		},
	]

	for acct in general_accounts:
		if not frappe.db.exists("Church Account", {"account_name": acct["account_name"]}):
			doc = frappe.get_doc({"doctype": "Church Account", "enabled": 1, **acct})
			doc.insert(ignore_permissions=True)

	frappe.db.commit()

	# 3. Create Income, Expense, and Fund accounts for every default department
	department_names = frappe.get_all("Church Department", filters={"enabled": 1}, pluck="department_name")
	for dept_name in department_names:
		create_department_accounts(dept_name)

	sync_department_account_tags()


def create_church_expense_workflow():
	available_actions = set(frappe.get_all("Workflow Action Master", pluck="name"))
	rework_action = next(
		(
			action
			for action in ("Changes Made", "Submit Changes", "Request Changes", "Make Changes", "Amend")
			if action in available_actions
		),
		"Submit",
	)

	workflow_states = {
		"Draft": "Warning",
		"Pending Approval": "Primary",
		"Approved": "Success",
		"Rejected": "Danger",
	}

	for state_name, style in workflow_states.items():
		if frappe.db.exists("Workflow State", state_name):
			frappe.db.set_value("Workflow State", state_name, "style", style, update_modified=False)
			continue

		frappe.get_doc(
			{
				"doctype": "Workflow State",
				"workflow_state_name": state_name,
				"style": style,
			}
		).insert(ignore_permissions=True)

	workflow_name = "Church Expense Approval"
	workflow = (
		frappe.get_doc("Workflow", workflow_name)
		if frappe.db.exists("Workflow", workflow_name)
		else frappe.new_doc("Workflow")
	)

	for name in frappe.get_all(
		"Workflow",
		filters={"document_type": "Church Expense", "name": ("!=", workflow_name)},
		pluck="name",
	):
		frappe.db.set_value("Workflow", name, "is_active", 0, update_modified=False)

	workflow.workflow_name = workflow_name
	workflow.document_type = "Church Expense"
	workflow.is_active = 1
	workflow.override_status = 0
	workflow.send_email_alert = 0
	workflow.workflow_state_field = "approval_status"
	workflow.states = []
	workflow.transitions = []

	for state in [
		{
			"state": "Draft",
			"doc_status": "0",
			"allow_edit": "Treasurer",
			"update_field": "approval_status",
			"update_value": "Draft",
			"send_email": 0,
		},
		{
			"state": "Pending Approval",
			"doc_status": "0",
			"allow_edit": "Pastor",
			"update_field": "approval_status",
			"update_value": "Pending Approval",
			"send_email": 0,
		},
		{
			"state": "Approved",
			"doc_status": "1",
			"allow_edit": "System Manager",
			"update_field": "approval_status",
			"update_value": "Approved",
			"send_email": 0,
		},
		{
			"state": "Rejected",
			"doc_status": "0",
			"allow_edit": "Treasurer",
			"update_field": "approval_status",
			"update_value": "Rejected",
			"send_email": 0,
		},
	]:
		workflow.append("states", state)

	for transition in [
		{
			"state": "Draft",
			"action": "Submit",
			"next_state": "Pending Approval",
			"allowed": "Treasurer",
			"allow_self_approval": 1,
		},
		{
			"state": "Draft",
			"action": "Submit",
			"next_state": "Pending Approval",
			"allowed": "System Manager",
			"allow_self_approval": 1,
		},
		{
			"state": "Pending Approval",
			"action": "Approve",
			"next_state": "Approved",
			"allowed": "Pastor",
			"allow_self_approval": 0,
		},
		{
			"state": "Pending Approval",
			"action": "Approve",
			"next_state": "Approved",
			"allowed": "Church Elder",
			"allow_self_approval": 0,
		},
		{
			"state": "Pending Approval",
			"action": "Approve",
			"next_state": "Approved",
			"allowed": "System Manager",
			"allow_self_approval": 1,
		},
		{
			"state": "Pending Approval",
			"action": "Reject",
			"next_state": "Rejected",
			"allowed": "Pastor",
			"allow_self_approval": 0,
		},
		{
			"state": "Pending Approval",
			"action": "Reject",
			"next_state": "Rejected",
			"allowed": "Church Elder",
			"allow_self_approval": 0,
		},
		{
			"state": "Pending Approval",
			"action": "Reject",
			"next_state": "Rejected",
			"allowed": "System Manager",
			"allow_self_approval": 1,
		},
		{
			"state": "Rejected",
			"action": rework_action,
			"next_state": "Draft",
			"allowed": "Treasurer",
			"allow_self_approval": 1,
		},
		{
			"state": "Rejected",
			"action": rework_action,
			"next_state": "Draft",
			"allowed": "System Manager",
			"allow_self_approval": 1,
		},
	]:
		workflow.append("transitions", transition)

	if workflow.is_new():
		workflow.insert(ignore_permissions=True)
	else:
		workflow.save(ignore_permissions=True)

	frappe.db.commit()
