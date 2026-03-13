# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.utils.nestedset import NestedSet


class ChurchAccount(NestedSet):
	nsm_parent_field = "parent_account"

	def before_save(self):
		# Recompute and persist balance whenever a leaf account is saved
		if not self.is_group:
			self.balance = _compute_leaf_balance(self.name)


# ---------------------------------------------------------------------------
# Balance computation helpers
# ---------------------------------------------------------------------------

# Maps specific Church Account names → the Tithe & Offering Entry field
# whose submitted totals represent that account's income.
_TOE_FIELD_MAP = {
	"Tithe Income": "tithe",
	"Regular Offering Income": "offering_local_amount",
	"Building Fund Income": "church_building_fund",
	"Camp Meeting Income": "camp_meeting",
}


def _get_all_leaf_balances():
	"""
	Return a dict {account_name: balance} computed from submitted transactions.

	Sources:
	  1. Church Expense (expense accounts & asset paid_from)
	  2. Tithe Offering Item child table (income accounts via Offering Type)
	  3. Standard Tithe & Offering Entry fields (named income accounts)
	"""
	balances = {}

	# 1a. Expense side of Church Expense → add to expense account balance
	for row in frappe.db.sql(
		"""
		SELECT account, SUM(amount) AS total
		FROM `tabChurch Expense`
		WHERE docstatus = 1
		  AND account IS NOT NULL AND account != ''
		GROUP BY account
		""",
		as_dict=True,
	):
		balances[row.account] = balances.get(row.account, 0) + flt(row.total)

	# 1b. Payment side of Church Expense → reduce the asset account balance
	for row in frappe.db.sql(
		"""
		SELECT paid_from AS account, SUM(amount) AS total
		FROM `tabChurch Expense`
		WHERE docstatus = 1
		  AND paid_from IS NOT NULL AND paid_from != ''
		GROUP BY paid_from
		""",
		as_dict=True,
	):
		balances[row.account] = balances.get(row.account, 0) - flt(row.total)

	# 2. Tithe Offering Item → income accounts linked through Offering Type
	for row in frappe.db.sql(
		"""
		SELECT toi.account, SUM(toi.amount) AS total
		FROM `tabTithe Offering Item` toi
		JOIN `tabTithe and Offering Entry` toe ON toe.name = toi.parent
		WHERE toe.docstatus = 1
		  AND toi.account IS NOT NULL AND toi.account != ''
		GROUP BY toi.account
		""",
		as_dict=True,
	):
		balances[row.account] = balances.get(row.account, 0) + flt(row.total)

	# 3. Standard Tithe & Offering Entry fields → named income accounts
	for account_name, field in _TOE_FIELD_MAP.items():
		total = frappe.db.sql(
			f"SELECT SUM(`{field}`) FROM `tabTithe and Offering Entry` WHERE docstatus = 1"
		)[0][0]
		if total:
			balances[account_name] = balances.get(account_name, 0) + flt(total)

	return balances


def _compute_leaf_balance(account_name):
	return flt(_get_all_leaf_balances().get(account_name, 0))


def _compute_group_balance(lft, rgt, all_leaf_balances):
	"""Sum balances of all non-group descendants using nested-set bounds."""
	descendants = frappe.get_all(
		"Church Account",
		filters=[
			["lft", ">", lft],
			["rgt", "<", rgt],
			["is_group", "=", 0],
		],
		pluck="name",
	)
	return flt(sum(flt(all_leaf_balances.get(d, 0)) for d in descendants))


# ---------------------------------------------------------------------------
# Custom get_children for the tree view (returns balances with each node)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_children(doctype, parent="", is_root=False, **kwargs):
	"""
	Returns the immediate children of `parent` with computed balances.

	Registered as get_tree_nodes in church_account_tree.js so that the tree
	view calls this instead of the default frappe.desk.treeview.get_children.

	Uses ifnull(parent_account,'') so that root accounts stored as NULL are
	correctly returned when parent is empty.
	"""
	parent = parent or ""

	# Use raw SQL via frappe.db.sql to support ifnull() in WHERE clause
	children = frappe.db.sql(
		"""
		SELECT
			name          AS value,
			name          AS title,
			is_group      AS expandable,
			account_type,
			account_subtype,
			lft,
			rgt
		FROM `tabChurch Account`
		WHERE ifnull(parent_account, '') = %(parent)s
		  AND docstatus < 2
		ORDER BY account_type, name
		""",
		{"parent": parent},
		as_dict=True,
	)

	if not children:
		return children

	# Compute all leaf balances in a single pass to avoid N+1 queries
	all_leaf_balances = _get_all_leaf_balances()

	for node in children:
		if node.get("expandable"):
			node["balance"] = _compute_group_balance(
				node["lft"], node["rgt"], all_leaf_balances
			)
		else:
			node["balance"] = flt(all_leaf_balances.get(node["value"], 0))

	return children


# ---------------------------------------------------------------------------
# Utility: refresh stored balances on all accounts
# ---------------------------------------------------------------------------

@frappe.whitelist()
def refresh_all_balances(silent=False):
	"""
	Recompute and persist the `balance` field on every Church Account.
	Callable from bench console or the tree-view toolbar button.
	"""
	all_leaf_balances = _get_all_leaf_balances()

	accounts = frappe.get_all(
		"Church Account",
		fields=["name", "is_group", "lft", "rgt"],
	)

	for acct in accounts:
		if acct.is_group:
			bal = _compute_group_balance(acct.lft, acct.rgt, all_leaf_balances)
		else:
			bal = flt(all_leaf_balances.get(acct.name, 0))

		frappe.db.set_value("Church Account", acct.name, "balance", bal, update_modified=False)

	frappe.db.commit()
	if not silent:
		frappe.msgprint("Account balances refreshed successfully.", alert=True)
