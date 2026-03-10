# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChurchDepartment(Document):
	def after_insert(self):
		if self.enabled:
			self._create_accounts()

	def on_update(self):
		if self.enabled:
			self._create_accounts()

	def _create_accounts(self):
		try:
			from stewardpro.church_finance.utils import create_department_accounts

			create_department_accounts(self.department_name)
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				f"Failed to create accounts for department: {self.department_name}",
			)
