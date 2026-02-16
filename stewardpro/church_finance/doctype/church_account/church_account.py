# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet


class ChurchAccount(NestedSet):
	nsm_parent_field = "parent_account"
