# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime


def send_weekly_sms_notification():
	"""
	Scheduled job to send SMS notifications every Saturday at midnight (00:00)
	This job runs if SMS integration is enabled in StewardPro Settings
	"""
	try:
		# Get SMS settings
		settings = frappe.get_single('StewardPro Settings')
		
		# Check if SMS is enabled
		if not settings.enable_sms_integration:
			frappe.logger().info("SMS integration is disabled. Skipping weekly SMS job.")
			return
		
		# Check if SMS configuration is complete
		if not settings.sms_api_key or not settings.sms_api_secret or not settings.sms_sender_id or not settings.sms_base_url:
			frappe.logger().warning("SMS configuration is incomplete. Skipping weekly SMS job.")
			return
		
		frappe.logger().info("Weekly SMS notification job executed successfully.")
		
		# TODO: Add your SMS sending logic here
		# Example: Send reminders, notifications, etc.
		
	except frappe.DoesNotExistError:
		frappe.logger().warning("StewardPro Settings not found. Skipping weekly SMS job.")
	except Exception as e:
		frappe.logger().error(f"Error in weekly SMS notification job: {str(e)}")

