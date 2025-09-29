# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_months, get_first_day, get_last_day, getdate, add_days
from datetime import datetime


def create_monthly_remittance():
	"""Create monthly remittance documents automatically"""
	try:
		# Check if automatic remittance is enabled
		if not should_create_automatic_remittance():
			frappe.logger().info("Automatic remittance creation is disabled")
			return

		# Get the previous month's date range
		today = getdate()
		previous_month_start = get_first_day(add_months(today, -1))
		previous_month_end = get_last_day(add_months(today, -1))

		# Create remittance for the previous month
		remittance_name = create_remittance_for_period(
			period_start=previous_month_start,
			period_end=previous_month_end,
			remittance_period="Monthly"
		)

		if remittance_name:
			frappe.logger().info(f"Monthly remittance {remittance_name} created for period {previous_month_start} to {previous_month_end}")
			send_remittance_notification(remittance_name, "Monthly")

	except Exception as e:
		frappe.logger().error(f"Error creating monthly remittance: {str(e)}")
		frappe.log_error(frappe.get_traceback(), "Monthly Remittance Creation Error")


def create_weekly_remittance():
	"""Create weekly remittance documents automatically"""
	try:
		# Check if automatic remittance is enabled and frequency is weekly
		if not should_create_automatic_remittance() or get_remittance_frequency() != "Weekly":
			frappe.logger().info("Weekly automatic remittance creation is disabled or not configured")
			return

		# Get the previous week's date range
		today = getdate()
		previous_week_end = add_days(today, -7)  # Last week's end
		previous_week_start = add_days(previous_week_end, -6)  # Last week's start

		# Create remittance for the previous week
		remittance_name = create_remittance_for_period(
			period_start=previous_week_start,
			period_end=previous_week_end,
			remittance_period="Weekly"
		)

		if remittance_name:
			frappe.logger().info(f"Weekly remittance {remittance_name} created for period {previous_week_start} to {previous_week_end}")
			send_remittance_notification(remittance_name, "Weekly")

	except Exception as e:
		frappe.logger().error(f"Error creating weekly remittance: {str(e)}")
		frappe.log_error(frappe.get_traceback(), "Weekly Remittance Creation Error")


def create_remittance_for_period(period_start, period_end, remittance_period):
	"""Create remittance document for a specific period"""
	
	# Check if remittance already exists for this period
	existing_remittance = frappe.db.exists("Remittance", {
		"remittance_period": remittance_period,
		"remittance_date": ["between", [period_start, period_end]]
	})
	
	if existing_remittance:
		frappe.logger().info(f"Remittance already exists for {remittance_period} period {period_start} to {period_end}")
		return
	
	# Get tithes and offerings data for the period
	contributions_data = get_contributions_for_period(period_start, period_end)
	
	if not contributions_data or (
		not contributions_data.get("total_tithe") and 
		not contributions_data.get("total_offering_to_field") and 
		not contributions_data.get("total_special_offerings")
	):
		frappe.logger().info(f"No contributions found for {remittance_period} period {period_start} to {period_end}")
		return
	
	# Get default organization settings
	organization_settings = get_default_organization_settings()
	
	# Create remittance document
	remittance = frappe.get_doc({
		"doctype": "Remittance",
		"remittance_date": period_end,
		"remittance_period": remittance_period,
		"status": "Draft",
		"organization_type": organization_settings.get("organization_type", "Conference"),
		"organization_name": organization_settings.get("organization_name", "Default Conference"),
		"contact_person": organization_settings.get("contact_person", ""),
		"contact_details": organization_settings.get("contact_details", ""),
		"tithe_amount": contributions_data.get("total_tithe", 0),
		"offering_to_field_amount": contributions_data.get("total_offering_to_field", 0),
		"special_offerings_amount": contributions_data.get("total_special_offerings", 0),
		"other_remittances_amount": 0,
		"payment_mode": organization_settings.get("default_payment_mode", "Bank Transfer"),
		"prepared_by": "Administrator"
	})
	
	# Add remittance items
	add_remittance_items(remittance, contributions_data, period_start, period_end)
	
	# Insert the remittance document
	remittance.insert(ignore_permissions=True)
	
	# Auto-submit if configured
	if organization_settings.get("auto_submit_remittance", False):
		remittance.submit()
	
	frappe.db.commit()
	
	frappe.logger().info(f"Created remittance {remittance.name} for {remittance_period} period {period_start} to {period_end}")
	
	return remittance.name


def get_contributions_for_period(period_start, period_end):
	"""Get aggregated contributions data for a specific period"""
	
	contributions = frappe.db.sql("""
		SELECT 
			SUM(tithe_amount) as total_tithe,
			SUM(offering_to_field) as total_offering_to_field,
			SUM(campmeeting_offering + church_building_offering) as total_special_offerings,
			COUNT(*) as total_records
		FROM `tabTithes and Offerings`
		WHERE date BETWEEN %s AND %s
		AND docstatus = 1
	""", (period_start, period_end), as_dict=True)
	
	if contributions:
		return contributions[0]
	
	return {}


def add_remittance_items(remittance, contributions_data, period_start, period_end):
	"""Add detailed remittance items to the remittance document"""
	
	# Add tithe item
	if contributions_data.get("total_tithe", 0) > 0:
		remittance.append("remittance_items", {
			"item_type": "Tithe",
			"description": f"Tithe remittance for period {period_start} to {period_end}",
			"amount": contributions_data.get("total_tithe", 0),
			"percentage": 100,
			"period_from": period_start,
			"period_to": period_end
		})
	
	# Add offering to field item
	if contributions_data.get("total_offering_to_field", 0) > 0:
		remittance.append("remittance_items", {
			"item_type": "Offering to Field",
			"description": f"Regular offering to field (58%) for period {period_start} to {period_end}",
			"amount": contributions_data.get("total_offering_to_field", 0),
			"percentage": 58,
			"period_from": period_start,
			"period_to": period_end
		})
	
	# Add special offerings item
	if contributions_data.get("total_special_offerings", 0) > 0:
		remittance.append("remittance_items", {
			"item_type": "Special Offering",
			"description": f"Special offerings (Camp meeting, Church building) for period {period_start} to {period_end}",
			"amount": contributions_data.get("total_special_offerings", 0),
			"percentage": 100,
			"period_from": period_start,
			"period_to": period_end
		})


def get_default_organization_settings():
	"""Get default organization settings for remittance"""

	# Try to get from StewardPro Settings (if exists) or use defaults
	settings = {}

	# Check if there's a StewardPro Settings doctype
	if frappe.db.exists("DocType", "StewardPro Settings"):
		try:
			stewardpro_settings = frappe.get_single("StewardPro Settings")
			settings = stewardpro_settings.get_organization_settings()
		except Exception:
			# Fallback to manual settings if method doesn't exist
			settings = {
				"organization_type": stewardpro_settings.get("default_organization_type", "Conference"),
				"organization_name": stewardpro_settings.get("default_organization_name", "Default Conference"),
				"contact_person": stewardpro_settings.get("default_contact_person", ""),
				"contact_details": stewardpro_settings.get("default_contact_details", ""),
				"default_payment_mode": stewardpro_settings.get("default_payment_mode", "Bank Transfer"),
				"auto_submit_remittance": stewardpro_settings.get("auto_submit_remittance", False)
			}
	else:
		# Use default settings
		settings = {
			"organization_type": "Conference",
			"organization_name": "Default Conference",
			"contact_person": "",
			"contact_details": "",
			"default_payment_mode": "Bank Transfer",
			"auto_submit_remittance": False
		}

	return settings


@frappe.whitelist()
def create_manual_remittance(period_start, period_end, remittance_period="Monthly"):
	"""Manually create remittance for a specific period"""
	
	if not period_start or not period_end:
		frappe.throw("Period start and end dates are required")
	
	period_start = getdate(period_start)
	period_end = getdate(period_end)
	
	if period_start > period_end:
		frappe.throw("Period start date cannot be after period end date")
	
	remittance_name = create_remittance_for_period(period_start, period_end, remittance_period)
	
	if remittance_name:
		frappe.msgprint(f"Remittance {remittance_name} created successfully for period {period_start} to {period_end}")
		return remittance_name
	else:
		frappe.msgprint("No remittance created. Check if contributions exist for the specified period.")
		return None


@frappe.whitelist()
def get_remittance_preview(period_start, period_end):
	"""Get preview of remittance data for a specific period"""
	
	if not period_start or not period_end:
		frappe.throw("Period start and end dates are required")
	
	period_start = getdate(period_start)
	period_end = getdate(period_end)
	
	contributions_data = get_contributions_for_period(period_start, period_end)
	
	if not contributions_data:
		return {"message": "No contributions found for the specified period"}
	
	preview = {
		"period_start": period_start,
		"period_end": period_end,
		"total_tithe": contributions_data.get("total_tithe", 0),
		"total_offering_to_field": contributions_data.get("total_offering_to_field", 0),
		"total_special_offerings": contributions_data.get("total_special_offerings", 0),
		"total_remittance": (
			contributions_data.get("total_tithe", 0) + 
			contributions_data.get("total_offering_to_field", 0) + 
			contributions_data.get("total_special_offerings", 0)
		),
		"total_records": contributions_data.get("total_records", 0)
	}
	
	return preview


def should_create_automatic_remittance():
	"""Check if automatic remittance creation is enabled"""
	try:
		if frappe.db.exists("DocType", "StewardPro Settings"):
			settings = frappe.get_single("StewardPro Settings")
			return settings.enable_automatic_remittance
	except Exception:
		pass
	return False


def get_remittance_frequency():
	"""Get the configured remittance frequency"""
	try:
		if frappe.db.exists("DocType", "StewardPro Settings"):
			settings = frappe.get_single("StewardPro Settings")
			return settings.remittance_frequency
	except Exception:
		pass
	return "Monthly"


def send_remittance_notification(remittance_name, period_type):
	"""Send notification when remittance is created"""
	try:
		if not frappe.db.exists("DocType", "StewardPro Settings"):
			return

		settings = frappe.get_single("StewardPro Settings")

		if not settings.notify_on_remittance_creation:
			return

		remittance = frappe.get_doc("Remittance", remittance_name)

		# Prepare email content
		subject = f"New {period_type} Remittance Created - {remittance_name}"

		message = f"""
		<h3>New {period_type} Remittance Created</h3>
		<p><strong>Remittance Number:</strong> {remittance_name}</p>
		<p><strong>Organization:</strong> {remittance.organization_name}</p>
		<p><strong>Date:</strong> {remittance.remittance_date}</p>
		<p><strong>Total Amount:</strong> {frappe.format_value(remittance.total_remittance_amount, 'Currency')}</p>
		<p><strong>Status:</strong> {remittance.status}</p>

		<h4>Breakdown:</h4>
		<ul>
			<li>Tithe Amount: {frappe.format_value(remittance.tithe_amount, 'Currency')}</li>
			<li>Offering to Field: {frappe.format_value(remittance.offering_to_field_amount, 'Currency')}</li>
			<li>Special Offerings: {frappe.format_value(remittance.special_offerings_amount, 'Currency')}</li>
		</ul>

		<p><a href="{frappe.utils.get_url()}/app/remittance/{remittance_name}">View Remittance</a></p>
		"""

		# Send to notification email
		if settings.remittance_notification_email:
			frappe.sendmail(
				recipients=[settings.remittance_notification_email],
				subject=subject,
				message=message
			)

		# Send summary to additional recipients
		if settings.send_remittance_summary and settings.summary_recipients:
			recipients = [email.strip() for email in settings.summary_recipients.split(",")]
			frappe.sendmail(
				recipients=recipients,
				subject=f"{period_type} Remittance Summary - {remittance_name}",
				message=message
			)

		frappe.logger().info(f"Remittance notification sent for {remittance_name}")

	except Exception as e:
		frappe.logger().error(f"Error sending remittance notification: {str(e)}")
		frappe.log_error(frappe.get_traceback(), "Remittance Notification Error")
