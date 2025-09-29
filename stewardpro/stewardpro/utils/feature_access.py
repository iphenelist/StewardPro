# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def check_feature_access(feature, raise_exception=True):
	"""
	Check if a feature is accessible based on current subscription
	
	Args:
		feature (str): Feature name (sms, mobile_money, advanced_analytics, etc.)
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
				'mobile_money': 'Mobile Money Integration',
				'advanced_analytics': 'Advanced Analytics',
				'multi_branch': 'Multi-Branch Management',
				'api_access': 'API Access',
				'custom_reports': 'Custom Reports',
				'white_label': 'White Label Options'
			}
			
			feature_name = feature_names.get(feature, feature.title())
			
			if settings.subscription_status in ['Expired', 'Suspended']:
				frappe.throw(
					_("Your subscription has {0}. Please renew to access {1}.").format(
						settings.subscription_status.lower(), feature_name
					),
					title=_("Subscription {0}").format(settings.subscription_status)
				)
			else:
				package_requirements = {
					'sms': ['Premium', 'Enterprise'],
					'mobile_money': ['Premium', 'Enterprise'],
					'advanced_analytics': ['Professional', 'Premium', 'Enterprise'],
					'multi_branch': ['Premium', 'Enterprise'],
					'api_access': ['Premium', 'Enterprise'],
					'custom_reports': ['Professional', 'Premium', 'Enterprise'],
					'white_label': ['Enterprise']
				}
				
				required_packages = package_requirements.get(feature, ['Premium', 'Enterprise'])
				
				frappe.throw(
					_("{0} is not available in your current {1} package. Please upgrade to {2}.").format(
						feature_name, 
						settings.subscription_package,
						' or '.join(required_packages)
					),
					title=_("Feature Not Available")
				)
		
		return has_access
		
	except frappe.DoesNotExistError:
		# Settings don't exist, create default
		from stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings import get_stewardpro_settings
		get_stewardpro_settings()
		return False


def check_sms_access(sms_count=1, raise_exception=True):
	"""
	Check if SMS can be sent
	
	Args:
		sms_count (int): Number of SMS to send
		raise_exception (bool): Whether to raise exception if access denied
	
	Returns:
		tuple: (bool, str) - (can_send, message)
	"""
	if not check_feature_access('sms', raise_exception=False):
		if raise_exception:
			check_feature_access('sms', raise_exception=True)
		return False, "SMS feature not available"
	
	try:
		settings = frappe.get_single('StewardPro Settings')
		can_send, message = settings.can_send_sms(sms_count)
		
		if not can_send and raise_exception:
			frappe.throw(_(message), title=_("SMS Quota Exceeded"))
		
		return can_send, message
		
	except Exception as e:
		if raise_exception:
			frappe.throw(str(e))
		return False, str(e)


def check_mobile_money_access(raise_exception=True):
	"""
	Check if mobile money integration is accessible
	
	Args:
		raise_exception (bool): Whether to raise exception if access denied
	
	Returns:
		bool: True if accessible, False otherwise
	"""
	return check_feature_access('mobile_money', raise_exception)


def check_member_limit(raise_exception=True):
	"""
	Check if member limit has been reached
	
	Args:
		raise_exception (bool): Whether to raise exception if limit reached
	
	Returns:
		bool: True if under limit, False if limit reached
	"""
	try:
		settings = frappe.get_single('StewardPro Settings')
		
		if settings.max_members == -1:  # Unlimited
			return True
		
		current_count = frappe.db.count('Member', {'status': "Active"})
		
		if current_count >= settings.max_members:
			if raise_exception:
				frappe.throw(
					_("Member limit reached ({0}/{1}). Please upgrade your subscription to add more members.").format(
						current_count, settings.max_members
					),
					title=_("Member Limit Reached")
				)
			return False
		
		return True
		
	except frappe.DoesNotExistError:
		return True  # No limits if settings don't exist


def get_subscription_info():
	"""
	Get current subscription information
	
	Returns:
		dict: Subscription details
	"""
	try:
		settings = frappe.get_single('StewardPro Settings')
		return {
			'package': settings.subscription_package,
			'status': settings.subscription_status,
			'start_date': settings.subscription_start_date,
			'end_date': settings.subscription_end_date,
			'max_members': settings.max_members,
			'current_members': settings.current_member_count,
			'features': {
				'sms': settings.enable_sms_integration,
				'mobile_money': settings.enable_mobile_money_integration,
				'advanced_analytics': settings.enable_advanced_analytics,
				'multi_branch': settings.enable_multi_branch,
				'api_access': settings.enable_api_access,
				'custom_reports': settings.enable_custom_reports,
				'white_label': settings.enable_white_label
			}
		}
	except frappe.DoesNotExistError:
		return {
			'package': 'Starter',
			'status': 'Trial',
			'features': {}
		}


def increment_sms_usage(count=1):
	"""
	Increment SMS usage counter
	
	Args:
		count (int): Number of SMS sent
	"""
	try:
		settings = frappe.get_single('StewardPro Settings')
		settings.increment_sms_usage(count)
	except frappe.DoesNotExistError:
		pass  # Ignore if settings don't exist


def get_feature_limits():
	"""
	Get current feature limits based on subscription
	
	Returns:
		dict: Feature limits
	"""
	try:
		settings = frappe.get_single('StewardPro Settings')
		return {
			'max_members': settings.max_members,
			'max_departments': settings.max_departments,
			'max_budget_items': settings.max_budget_items,
			'max_reports_per_month': settings.max_reports_per_month,
			'storage_limit_gb': settings.storage_limit_gb,
			'api_calls_per_month': settings.api_calls_per_month,
			'export_limit_per_month': settings.export_limit_per_month,
			'data_retention_months': settings.data_retention_months,
			'sms_monthly_quota': settings.sms_monthly_quota,
			'sms_used_this_month': settings.sms_used_this_month
		}
	except frappe.DoesNotExistError:
		return {
			'max_members': 200,
			'max_departments': 10,
			'max_budget_items': 100,
			'max_reports_per_month': 50,
			'storage_limit_gb': 5,
			'api_calls_per_month': 1000,
			'export_limit_per_month': 20,
			'data_retention_months': 24,
			'sms_monthly_quota': 0,
			'sms_used_this_month': 0
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


# Decorator for SMS access checking
def requires_sms(sms_count=1):
	"""
	Decorator to check SMS access before executing function
	
	Args:
		sms_count (int): Number of SMS to send
	
	Usage:
		@requires_sms(5)
		def send_bulk_sms():
			pass
	"""
	def decorator(func):
		def wrapper(*args, **kwargs):
			check_sms_access(sms_count, raise_exception=True)
			return func(*args, **kwargs)
		return wrapper
	return decorator


# Decorator for member limit checking
def requires_member_limit():
	"""
	Decorator to check member limit before adding new members
	
	Usage:
		@requires_member_limit()
		def create_member():
			pass
	"""
	def decorator(func):
		def wrapper(*args, **kwargs):
			check_member_limit(raise_exception=True)
			return func(*args, **kwargs)
		return wrapper
	return decorator
