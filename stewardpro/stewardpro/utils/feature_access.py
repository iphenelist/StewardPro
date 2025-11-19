# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def check_feature_access(feature, raise_exception=True):
	"""
	Check if a feature is accessible based on simple checkbox flags

	Args:
		feature (str): Feature name (sms, mobile_money)
		raise_exception (bool): Whether to raise exception if access denied

	Returns:
		bool: True if feature is accessible, False otherwise
	"""
	try:
		settings = frappe.get_single('StewardPro Settings')
		has_access = settings.is_feature_enabled(feature)

		if not has_access and raise_exception:
			feature_names = {
				'sms': 'SMS Integration',
				'mobile_money': 'Mobile Money Integration'
			}

			feature_name = feature_names.get(feature, feature.title())
			frappe.throw(
				_("{0} is not enabled in settings.").format(feature_name),
				title=_("Feature Not Enabled")
			)

		return has_access

	except frappe.DoesNotExistError:
		# Settings don't exist, create default
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import get_stewardpro_settings
		get_stewardpro_settings()
		return False





def check_mobile_money_access(raise_exception=True):
	"""
	Check if mobile money integration is accessible
	
	Args:
		raise_exception (bool): Whether to raise exception if access denied
	
	Returns:
		bool: True if accessible, False otherwise
	"""
	return check_feature_access('mobile_money', raise_exception)


def get_subscription_info():
	"""
	Get current feature configuration

	Returns:
		dict: Feature settings
	"""
	try:
		settings = frappe.get_single('StewardPro Settings')
		return {
			'features': {
				'sms': settings.enable_sms_integration,
				'mobile_money': settings.enable_mobile_money_integration
			}
		}
	except frappe.DoesNotExistError:
		return {
			'features': {
				'sms': False,
				'mobile_money': False
			}
		}





# Decorator for feature access checking
def requires_feature(feature):
	"""
	Decorator to check feature access before executing function
	
	Args:
		feature (str): Feature name to check
	
	Usage:
		@requires_feature('sms')
		def send_sms():
			pass
	"""
	def decorator(func):
		def wrapper(*args, **kwargs):
			check_feature_access(feature, raise_exception=True)
			return func(*args, **kwargs)
		return wrapper
	return decorator


