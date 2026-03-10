# Copyright (c) 2026, StewardPro and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, now_datetime, fmt_money, getdate
from frappe.query_builder import DocType
from frappe.query_builder.functions import Function


class Month(Function):
	"""MySQL MONTH() function for frappe.qb"""
	def __init__(self, term, alias=None):
		super().__init__("MONTH", term, alias=alias)


class Day(Function):
	"""MySQL DAY() function for frappe.qb"""
	def __init__(self, term, alias=None):
		super().__init__("DAY", term, alias=alias)


def is_sms_enabled():
	"""Check if SMS is enabled in Church Settings"""
	return frappe.db.get_single_value("Church Settings", "enable_sms")


def get_sms_client():
	"""Get NotifyAfrica client using credentials from Church Settings"""
	from frappe.utils.password import get_decrypted_password
	api_token = get_decrypted_password(
		"Church Settings", "Church Settings", "sms_api_token"
	)
	if not api_token:
		frappe.log_error("SMS API Token not configured in Church Settings", "SMS Error")
		return None

	try:
		from notify_africa import NotifyAfrica
		return NotifyAfrica(apiToken=api_token)
	except ImportError:
		frappe.log_error("notify_africa package is not installed. Run: pip install notify_africa", "SMS Error")
		return None


def send_sms(phone_number, message, reference_doctype=None, reference_name=None, recipient_name=None):
	"""Core SMS sending function with logging"""
	if not is_sms_enabled():
		return None

	if not phone_number:
		return None

	client = get_sms_client()
	if not client:
		return None

	sender_id = frappe.db.get_single_value("Church Settings", "sms_sender_id")
	if not sender_id:
		frappe.log_error("SMS Sender ID not configured in Church Settings", "SMS Error")
		return None

	try:
		from notify_africa.exceptions import NotifyAfricaException, NetworkError

		send_response = client.send_single_message(
			phoneNumber=phone_number,
			message=message,
			senderId=sender_id,
		)

		log_sms(
			recipient=phone_number,
			recipient_name=recipient_name,
			message=message,
			status="Sent",
			message_id=getattr(send_response, "messageId", ""),
			reference_doctype=reference_doctype,
			reference_name=reference_name,
		)
		return send_response

	except (NotifyAfricaException, NetworkError) as e:
		log_sms(
			recipient=phone_number,
			recipient_name=recipient_name,
			message=message,
			status="Failed",
			reference_doctype=reference_doctype,
			reference_name=reference_name,
			error_message=str(e),
		)
		frappe.log_error(f"SMS send failed to {phone_number}: {e}", "SMS Error")
		return None
	except ImportError:
		frappe.log_error("notify_africa package is not installed", "SMS Error")
		return None


def log_sms(recipient, message, status, recipient_name=None, message_id=None,
			reference_doctype=None, reference_name=None, error_message=None):
	"""Create an SMS Log record"""
	try:
		log = frappe.new_doc("SMS Log")
		log.recipient = recipient
		log.recipient_name = recipient_name or ""
		log.message = message
		log.status = status
		log.message_id = message_id or ""
		log.reference_doctype = reference_doctype or ""
		log.reference_name = reference_name or ""
		log.sent_at = now_datetime()
		log.error_message = error_message or ""
		log.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		frappe.log_error(f"Failed to create SMS Log: {e}", "SMS Log Error")


def send_tithe_offering_receipt(doc):
	"""Called from TitheandOfferingEntry.on_submit to send receipt SMS"""
	if not is_sms_enabled():
		return

	if not frappe.db.get_single_value("Church Settings", "enable_tithe_offering_sms"):
		return

	if not doc.member:
		return

	ChurchMember = DocType("Church Member")
	member_data = (
		frappe.qb.from_(ChurchMember)
		.select(ChurchMember.phone)
		.where(ChurchMember.name == doc.member)
	).run(as_dict=True)

	if not member_data or not member_data[0].phone:
		return

	template = frappe.db.get_single_value("Church Settings", "tithe_offering_sms_template")
	if not template:
		return

	church_name = frappe.db.get_single_value("Church Settings", "church_name") or "Our Church"
	currency = frappe.db.get_single_value("Church Settings", "currency") or "TZS"

	message = template.format(
		member_name=doc.member_name or doc.member,
		amount=fmt_money(doc.grand_total, currency=currency),
		date=frappe.utils.formatdate(doc.entry_date),
		church_name=church_name,
	)

	send_sms(
		phone_number=member_data[0].phone,
		message=message,
		reference_doctype="Tithe and Offering Entry",
		reference_name=doc.name,
		recipient_name=doc.member_name,
	)


def send_member_welcome(doc):
	"""Called from ChurchMember.after_insert to send welcome SMS"""
	if not is_sms_enabled():
		return

	if not frappe.db.get_single_value("Church Settings", "enable_member_welcome_sms"):
		return

	if not doc.phone:
		return

	template = frappe.db.get_single_value("Church Settings", "member_welcome_sms_template")
	if not template:
		return

	church_name = frappe.db.get_single_value("Church Settings", "church_name") or "Our Church"

	message = template.format(
		member_name=doc.full_name or f"{doc.first_name} {doc.last_name}",
		church_name=church_name,
	)

	send_sms(
		phone_number=doc.phone,
		message=message,
		reference_doctype="Church Member",
		reference_name=doc.name,
		recipient_name=doc.full_name,
	)


def send_birthday_greetings():
	"""Scheduled daily: send birthday SMS to members whose birthday is today"""
	if not is_sms_enabled():
		return

	if not frappe.db.get_single_value("Church Settings", "enable_birthday_sms"):
		return

	template = frappe.db.get_single_value("Church Settings", "birthday_sms_template")
	if not template:
		return

	church_name = frappe.db.get_single_value("Church Settings", "church_name") or "Our Church"
	today_date = getdate(today())

	ChurchMemberT = DocType("Church Member")
	members = (
		frappe.qb.from_(ChurchMemberT)
		.select(
			ChurchMemberT.name,
			ChurchMemberT.full_name,
			ChurchMemberT.phone,
			ChurchMemberT.date_of_birth,
		)
		.where(ChurchMemberT.membership_status == "Active")
		.where(ChurchMemberT.phone.isnotnull())
		.where(ChurchMemberT.phone != "")
		.where(ChurchMemberT.date_of_birth.isnotnull())
		.where(Month(ChurchMemberT.date_of_birth) == today_date.month)
		.where(Day(ChurchMemberT.date_of_birth) == today_date.day)
	).run(as_dict=True)

	for member in members:
		message = template.format(
			member_name=member.full_name or member.name,
			church_name=church_name,
		)

		send_sms(
			phone_number=member.phone,
			message=message,
			reference_doctype="Church Member",
			reference_name=member.name,
			recipient_name=member.full_name,
		)
