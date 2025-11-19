# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe import _


def get_mobile_money_settings():
	"""Get Mobile Money settings from StewardPro Settings"""
	try:
		settings = frappe.get_single('StewardPro Settings')
		if not settings.enable_mobile_money_integration:
			frappe.throw(_("Mobile Money Integration is not enabled in settings."), title=_("Mobile Money Not Enabled"))

		if not settings.money_api_key or not settings.money_public_key:
			frappe.throw(_("Mobile Money configuration is incomplete. Please configure Mobile Money settings."), title=_("Mobile Money Configuration Error"))

		if not settings.mobile_money_base_url:
			frappe.throw(_("Mobile Money Base URL is not configured. Please set the Mobile Money API endpoint."), title=_("Mobile Money Configuration Error"))

		return settings
	except frappe.DoesNotExistError:
		frappe.throw(_("StewardPro Settings not found."), title=_("Configuration Error"))


class MobileMoneyAPI:
	"""Mobile Money API integration for StewardPro"""

	def __init__(self):
		settings = get_mobile_money_settings()
		self.api_key = settings.money_api_key
		self.public_key = settings.money_public_key
		self.base_url = settings.mobile_money_base_url

	def send_payment_request(self, phone_number, amount, description=""):
		"""Send payment request via Mobile Money"""
		try:
			payload = {
				"api_key": self.api_key,
				"public_key": self.public_key,
				"phone_number": phone_number,
				"amount": amount,
				"description": description
			}

			headers = {
				"Content-Type": "application/json"
			}

			response = requests.post(
				self.base_url,
				headers=headers,
				data=json.dumps(payload),
				timeout=30
			)

			if response.status_code == 200:
				result = response.json()
				frappe.logger().info(f"Mobile Money payment request sent: {result}")
				return {"success": True, "response": result}
			else:
				frappe.logger().error(f"Mobile Money failed: {response.status_code} - {response.text}")
				return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

		except Exception as e:
			frappe.logger().error(f"Mobile Money API Error: {str(e)}")
			return {"success": False, "error": str(e)}


@frappe.whitelist()
def test_mobile_money_connection(**kwargs):
	"""Test Mobile Money API connection"""
	try:
		mobile_money_api = MobileMoneyAPI()
		test_phone = "255786540517"  # Test phone number
		test_amount = "1000"  # Test amount

		result = mobile_money_api.send_payment_request(test_phone, test_amount, "StewardPro Test")
		return result

	except Exception as e:
		return {"success": False, "error": str(e)}

