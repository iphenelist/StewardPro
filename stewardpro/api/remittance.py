# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, getdate, get_datetime, add_days


def create_weekly_remittance():
	"""
	Scheduled daily task that creates a Conference Remittance every Saturday night.

	Collects all submitted Tithe and Offering entries from Sunday through Saturday,
	aggregates the conference-bound amounts (tithe, offering conference share, and
	camp meeting), and saves a draft Conference Remittance document for the Treasurer
	to review and submit.

	Safe to run multiple times – skips creation if a remittance for the period
	already exists.
	"""
	now = get_datetime()

	# weekday(): Monday=0 … Saturday=5
	if now.weekday() != 5:
		return

	period_to = getdate(now)
	period_from = getdate(add_days(period_to, -6))  # Previous Sunday

	# Skip if a remittance for this exact period already exists (not cancelled)
	existing = frappe.db.exists(
		"Conference Remittance",
		{"period_from": period_from, "period_to": period_to, "docstatus": ["!=", 2]},
	)
	if existing:
		frappe.logger().info(
			f"Weekly remittance for {period_from} – {period_to} already exists "
			f"({existing}). Skipping."
		)
		return

	# Fetch all submitted Tithe and Offering entries within the period
	entries = frappe.get_all(
		"Tithe and Offering Entry",
		filters={
			"docstatus": 1,
			"entry_date": ["between", [period_from, period_to]],
		},
		fields=[
			"name",
			"tithe",
			"offering_conference_amount",
			"camp_meeting",
		],
	)

	if not entries:
		frappe.logger().info(
			f"No submitted Tithe & Offering entries found for {period_from} – {period_to}. "
			"Skipping remittance creation."
		)
		return

	# Aggregate per component
	total_tithe = flt(sum(flt(e.tithe) for e in entries))
	total_offering_conf = flt(sum(flt(e.offering_conference_amount) for e in entries))
	total_camp = flt(sum(flt(e.camp_meeting) for e in entries))

	if not (total_tithe or total_offering_conf or total_camp):
		frappe.logger().info(
			f"All conference amounts are zero for {period_from} – {period_to}. Skipping."
		)
		return

	# Build remittance line items using hardcoded Select values
	items = []
	if total_tithe:
		items.append({"offering_type": "Tithe", "amount": total_tithe})
	if total_offering_conf:
		items.append({"offering_type": "Sabbath School Offering", "amount": total_offering_conf})
	if total_camp:
		items.append({"offering_type": "Camp Meeting Offering", "amount": total_camp})

	if not items:
		return

	entry_count = len(entries)
	remittance = frappe.get_doc(
		{
			"doctype": "Conference Remittance",
			"remittance_date": period_to,
			"period_from": period_from,
			"period_to": period_to,
			"status": "Draft",
			"payment_method": "Bank Transfer",
			"remarks": (
				f"Auto-generated weekly remittance for {period_from} to {period_to}. "
				f"Based on {entry_count} Tithe & Offering "
				f"{'entry' if entry_count == 1 else 'entries'}."
			),
			"items": items,
		}
	)
	remittance.insert(ignore_permissions=True)
	frappe.db.commit()

	frappe.logger().info(
		f"Auto-created Conference Remittance {remittance.name} "
		f"for period {period_from} – {period_to} "
		f"(tithe={total_tithe}, offering_conf={total_offering_conf}, camp={total_camp})."
	)
