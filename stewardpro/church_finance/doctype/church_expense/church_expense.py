# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


APPROVAL_STATUSES = ("Draft", "Pending Approval", "Approved", "Rejected")


def _get_account(account_name):
	account = frappe.db.get_value(
		"Church Account",
		account_name,
		["name", "account_name", "account_type", "department", "enabled", "is_group"],
		as_dict=True,
	)
	if not account:
		frappe.throw(_("Church Account {0} was not found.").format(frappe.bold(account_name)))
	return account


def _refresh_related_finance(account_names=None, expense_date=None):
	from stewardpro.church_finance.doctype.church_account.church_account import refresh_all_balances
	from stewardpro.church_finance.doctype.church_budget.church_budget import refresh_expense_actuals

	refresh_all_balances(silent=True)
	refresh_expense_actuals(account_names=account_names, expense_date=expense_date)


def _account_search_conditions(searchfield):
	return f"""
		(
			name LIKE %(txt)s
			OR account_name LIKE %(txt)s
			OR IFNULL(description, '') LIKE %(txt)s
			OR IFNULL({searchfield}, '') LIKE %(txt)s
		)
	"""


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_expense_accounts(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("department"):
		return []

	return frappe.db.sql(
		f"""
		SELECT
			name,
			account_name,
			IFNULL(department, ''),
			IFNULL(description, '')
		FROM `tabChurch Account`
		WHERE docstatus < 2
		  AND enabled = 1
		  AND is_group = 0
		  AND account_type = 'Expense'
		  AND (IFNULL(department, '') = '' OR department = %(department)s)
		  AND {_account_search_conditions(searchfield)}
		ORDER BY
			CASE WHEN department = %(department)s THEN 0 ELSE 1 END,
			account_name
		LIMIT %(start)s, %(page_len)s
		""",
		{
			"department": filters.get("department"),
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len,
		},
	)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_paid_from_accounts(doctype, txt, searchfield, start, page_len, filters):
	params = {
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len,
	}
	department_condition = ""
	if filters.get("department"):
		params["department"] = filters.get("department")
		department_condition = "AND (IFNULL(department, '') = '' OR department = %(department)s)"

	return frappe.db.sql(
		f"""
		SELECT
			name,
			account_name,
			IFNULL(account_subtype, ''),
			IFNULL(description, '')
		FROM `tabChurch Account`
		WHERE docstatus < 2
		  AND enabled = 1
		  AND is_group = 0
		  AND account_type = 'Asset'
		  {department_condition}
		  AND {_account_search_conditions(searchfield)}
		ORDER BY account_subtype, account_name
		LIMIT %(start)s, %(page_len)s
		""",
		params,
	)


class ChurchExpense(Document):
	def validate(self):
		self.amount = flt(self.amount)
		self.approval_status = self.approval_status or "Draft"

		if self.approval_status not in APPROVAL_STATUSES:
			frappe.throw(_("Approval Status must be one of: {0}").format(", ".join(APPROVAL_STATUSES)))

		if self.amount <= 0:
			frappe.throw(_("Amount must be greater than zero."))

		self._validate_expense_account()
		self._validate_paid_from_account()

	def before_submit(self):
		self.approval_status = "Approved"
		self.approved_by = self.approved_by or frappe.session.user
		self.approved_on = self.approved_on or now_datetime()

	def on_submit(self):
		frappe.db.set_value(
			self.doctype,
			self.name,
			{
				"approval_status": "Approved",
				"approved_by": self.approved_by or frappe.session.user,
				"approved_on": self.approved_on or now_datetime(),
			},
			update_modified=False,
		)
		_refresh_related_finance(
			account_names=[self.account, self.paid_from],
			expense_date=self.expense_date,
		)

	def on_cancel(self):
		_refresh_related_finance(
			account_names=[self.account, self.paid_from],
			expense_date=self.expense_date,
		)

	def _validate_expense_account(self):
		account = _get_account(self.account)
		if account.account_type != "Expense":
			frappe.throw(_("Expense Account must be an Expense type Church Account."))
		if account.is_group:
			frappe.throw(_("Expense Account must be a leaf account, not a group account."))
		if not account.enabled:
			frappe.throw(_("Expense Account {0} is disabled.").format(frappe.bold(account.account_name)))
		if account.department and account.department != self.department:
			frappe.throw(
				_("Expense Account {0} belongs to {1}, not {2}.").format(
					frappe.bold(account.account_name),
					frappe.bold(account.department),
					frappe.bold(self.department),
				)
			)

	def _validate_paid_from_account(self):
		account = _get_account(self.paid_from)
		if account.account_type != "Asset":
			frappe.throw(_("Paid From Account must be an Asset type Church Account."))
		if account.is_group:
			frappe.throw(_("Paid From Account must be a leaf account, not a group account."))
		if not account.enabled:
			frappe.throw(_("Paid From Account {0} is disabled.").format(frappe.bold(account.account_name)))
		if account.department and account.department != self.department:
			frappe.throw(
				_("Paid From Account {0} belongs to {1}, not {2}.").format(
					frappe.bold(account.account_name),
					frappe.bold(account.department),
					frappe.bold(self.department),
				)
			)
