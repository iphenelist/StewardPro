
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import timedelta

class FiscalYear(Document):
	def validate(self):
		self.validate_dates()
		self.validate_overlap()
		self.disallow_date_change()

	def validate_dates(self):
		if not self.is_short_year:
			expected_end = frappe.utils.add_days(
				frappe.utils.add_months(self.year_start_date, 12), -1
			)
			if self.year_end_date != expected_end:
				frappe.throw(_("Year End Date must be exactly 12 months minus 1 day from Start Date unless 'Is Short/Long Year' is checked."))

	def validate_overlap(self):
		overlaps = frappe.db.sql("""
			SELECT name FROM `tabFiscal Year`
			WHERE (
				(year_start_date <= %s AND year_end_date >= %s)
				OR (year_start_date <= %s AND year_end_date >= %s)
				OR (year_start_date >= %s AND year_end_date <= %s)
			) AND name != %s
		""", (self.year_start_date, self.year_start_date, self.year_end_date, self.year_end_date, self.year_start_date, self.year_end_date, self.name))
		if overlaps:
			frappe.throw(_("Fiscal Year dates overlap with another Fiscal Year."))

	def disallow_date_change(self):
		if not self.is_new():
			old = frappe.get_doc("Fiscal Year", self.name)
			if old.year_start_date != self.year_start_date or old.year_end_date != self.year_end_date:
				frappe.throw(_("Cannot change Start or End Date after creation."))

	def on_update(self):
		self.check_duplicate_fiscal_year()
		frappe.cache().delete_value("fiscal_years")

	def on_trash(self):
		frappe.cache().delete_value("fiscal_years")

	def check_duplicate_fiscal_year(self):
		exists = frappe.db.exists("Fiscal Year", {
			"year_start_date": self.year_start_date,
			"year_end_date": self.year_end_date,
			"name": ["!=", self.name]
		})
		if exists:
			frappe.throw(_("Duplicate Fiscal Year with same start and end dates exists."))

@frappe.whitelist()
def get_from_and_to_date(fiscal_year):
	cached = frappe.cache().get_value("fiscal_years")
	if not cached:
		cached = {}
		for fy in frappe.get_all("Fiscal Year", fields=["name", "year_start_date", "year_end_date"]):
			cached[fy.name] = {"from_date": fy.year_start_date, "to_date": fy.year_end_date}
		frappe.cache().set_value("fiscal_years", cached)
	return cached.get(fiscal_year)


def auto_create_fiscal_year():
	today = frappe.utils.nowdate()
	ending_soon = frappe.db.get_all("Fiscal Year", fields=["name", "year_end_date"], filters={
		"year_end_date": ["=", frappe.utils.add_days(today, 3)]
	})
	for fy in ending_soon:
		doc = frappe.get_doc("Fiscal Year", fy.name)
		next_start = frappe.utils.add_days(doc.year_end_date, 1)
		next_end = frappe.utils.add_days(frappe.utils.add_months(next_start, 12), -1)
		next_year = f"{next_start.year}-{next_end.year}" if next_start.year != next_end.year else str(next_start.year)
		if not frappe.db.exists("Fiscal Year", next_year):
			new_fy = frappe.get_doc({
				"doctype": "Fiscal Year",
				"year": next_year,
				"year_start_date": next_start,
				"year_end_date": next_end,
				"auto_created": 1
			})
			new_fy.insert(ignore_permissions=True)
			frappe.msgprint(_(f"Auto-created Fiscal Year: {next_year}"))
