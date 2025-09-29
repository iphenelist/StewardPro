# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe import _
from frappe.utils import nowdate, fmt_money, getdate
from stewardpro.stewardpro.utils.feature_access import check_sms_access, increment_sms_usage, requires_sms


class SMSAPI:
    """SMS API integration for StewardPro"""

    def __init__(self):
        self.api_key = "sms_277f7f163c25066e20c0ddff48ec0062"
        self.api_secret = "8cf7c83332b1eb126b9b8ba2368967b251e77bd02e4ea8e02e7046cfaaadce43"
        self.sender_id = "Michongo"
        self.base_url = "https://onsms.co.tz/api/method/always_on_sms.api.sms.send_sms"

    def send_sms(self, recipients, message):
        """Send SMS using Beem Africa API"""
        try:
            # Ensure recipients is a list
            if isinstance(recipients, str):
                recipients = [recipients]

            # Clean phone numbers (ensure they start with 255 for Tanzania)
            clean_recipients = []
            for phone in recipients:
                phone = str(phone).strip()
                if phone.startswith('0'):
                    phone = '255' + phone[1:]
                elif phone.startswith('+255'):
                    phone = phone[1:]
                elif not phone.startswith('255'):
                    phone = '255' + phone
                clean_recipients.append(phone)

            payload = {
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "sender_id": self.sender_id,
                "message": message,
                "recipients": clean_recipients
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
                frappe.logger().info(f"SMS sent successfully: {result}")
                return {"success": True, "response": result}
            else:
                frappe.logger().error(f"SMS failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            frappe.logger().error(f"SMS API Error: {str(e)}")
            return {"success": False, "error": str(e)}


@frappe.whitelist()
@requires_sms(1)
def send_member_registration_sms(member_name, phone_number, **kwargs):
    """Send welcome SMS to newly registered member"""
    try:
        # Check SMS access and quota
        can_send, message = check_sms_access(1, raise_exception=True)

        sms_api = SMSAPI()

        # Create welcome message with length check
        base_message = "Welcome ! Your membership is registered. We're excited to have you join us. God bless! - Church Admin"
        if len(f"Welcome {member_name}! Your membership is registered. We're excited to have you join us. God bless! - Church Admin") <= 140:
            message = f"Welcome {member_name}! Your membership is registered. We're excited to have you join us. God bless! - Church Admin"
        else:
            # Use shorter template for long names
            message = f"Welcome {member_name}! Membership registered. God bless! - Church"
            # If still too long, truncate name
            if len(message) > 140:
                max_name_length = 140 - len("Welcome ! Membership registered. God bless! - Church")
                truncated_name = member_name[:max_name_length-3] + "..." if len(member_name) > max_name_length else member_name
                message = f"Welcome {truncated_name}! Membership registered. God bless! - Church"

        result = sms_api.send_sms([phone_number], message)

        if result["success"]:
            # Increment SMS usage counter
            increment_sms_usage(1)
            # Log the SMS
            create_sms_log("Member Registration", member_name, phone_number, message, "Success")
            return {"success": True, "message": "Welcome SMS sent successfully"}
        else:
            create_sms_log("Member Registration", member_name, phone_number, message, f"Failed: {result['error']}")
            return {"success": False, "error": result["error"]}

    except Exception as e:
        frappe.logger().error(f"Member registration SMS error: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
@requires_sms(1)
def send_tithe_offering_sms(member_name, phone_number, receipt_number, tithe_amount, offering_amount, total_amount, date, **kwargs):
    """Send receipt SMS for tithe and offering"""
    try:
        # Check SMS access and quota
        can_send, message = check_sms_access(1, raise_exception=True)

        sms_api = SMSAPI()

        # Format amounts
        tithe_formatted = fmt_money(tithe_amount) if tithe_amount else "0"
        offering_formatted = fmt_money(offering_amount) if offering_amount else "0"
        total_formatted = fmt_money(total_amount)

        # Create receipt message with length check
        date_str = getdate(date).strftime('%d/%m/%Y')
        full_message = f"Thank you {member_name}! Receipt #{receipt_number} {date_str} Total: {total_formatted}. God bless! - Church"

        if len(full_message) <= 140:
            message = full_message
        else:
            # Use shorter template
            short_message = f"Thank you {member_name}! Receipt #{receipt_number} Total: {total_formatted}. God bless!"
            if len(short_message) <= 140:
                message = short_message
            else:
                # Truncate name if still too long
                base_length = len(f"Thank you ! Receipt #{receipt_number} Total: {total_formatted}. God bless!")
                max_name_length = 140 - base_length
                truncated_name = member_name[:max_name_length-3] + "..." if len(member_name) > max_name_length else member_name
                message = f"Thank you {truncated_name}! Receipt #{receipt_number} Total: {total_formatted}. God bless!"

        result = sms_api.send_sms([phone_number], message)

        if result["success"]:
            # Increment SMS usage counter
            increment_sms_usage(1)
            # Log the SMS
            create_sms_log("Tithe & Offering Receipt", member_name, phone_number, message, "Success")
            return {"success": True, "message": "Receipt SMS sent successfully"}
        else:
            create_sms_log("Tithe & Offering Receipt", member_name, phone_number, message, f"Failed: {result['error']}")
            return {"success": False, "error": result["error"]}

    except Exception as e:
        frappe.logger().error(f"Tithe offering SMS error: {str(e)}")
        return {"success": False, "error": str(e)}


def create_sms_log(sms_type, recipient_name, phone_number, message, status):
    """Create SMS log entry"""
    try:
        # Clean up status message if it's too long or contains complex error details
        clean_status = clean_error_message(status)

        sms_log = frappe.get_doc({
            "doctype": "SMS Log",
            "sent_on": frappe.utils.now(),
            "sender": "Michongo",
            "receiver": phone_number,
            "message": message,
            "status": clean_status,
            "custom_sms_type": sms_type,
            "custom_recipient_name": recipient_name
        })
        sms_log.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.logger().error(f"SMS Log creation error: {str(e)}")


def clean_error_message(status):
    """Clean and shorten error messages for SMS log status"""
    if not status or status == "Success":
        return status

    # If it's a failed message, try to extract the meaningful part
    if status.startswith("Failed:"):
        error_part = status[7:].strip()  # Remove "Failed: " prefix

        # Try to extract meaningful error messages from common patterns
        import json
        import re

        try:
            # Check if it contains JSON error response
            if "HTTP 400:" in error_part:
                # Extract the main error message from HTTP response
                json_match = re.search(r'\{"message":\{"status":"error","message":"([^"]+)"', error_part)
                if json_match:
                    main_error = json_match.group(1)
                    return f"Failed: {main_error}"

            # Check for insufficient balance specifically
            if "Insufficient balance" in error_part:
                balance_match = re.search(r'Current balance: ([\d.]+) TZS', error_part)
                if balance_match:
                    balance = balance_match.group(1)
                    return f"Failed: Insufficient balance ({balance} TZS)"
                else:
                    return "Failed: Insufficient balance"

            # Check for other common error patterns
            if "Error processing request" in error_part:
                return "Failed: Error processing request"

            # If error is still too long, truncate it intelligently
            if len(error_part) > 200:
                return f"Failed: {error_part[:200]}..."

            return f"Failed: {error_part}"

        except Exception:
            # If parsing fails, just truncate the original message
            if len(status) > 250:
                return f"{status[:250]}..."
            return status

    # For non-failed messages, just ensure they're not too long
    if len(status) > 250:
        return f"{status[:250]}..."

    return status


@frappe.whitelist()
def send_bulk_welcome_sms(member_names, **kwargs):
    """Send welcome SMS to multiple members"""
    try:
        if isinstance(member_names, str):
            import json
            member_names = json.loads(member_names)

        # Check SMS access for bulk sending
        sms_count = len(member_names)
        can_send, message = check_sms_access(sms_count, raise_exception=True)

        results = []
        sms_api = SMSAPI()

        for member_name in member_names:
            try:
                # Get member details
                member_doc = frappe.get_doc("Member", member_name)

                if not member_doc.contact:
                    results.append({
                        "member": member_name,
                        "success": False,
                        "error": "No phone number"
                    })
                    continue

                # Send welcome SMS with length check
                full_message = f"Welcome {member_doc.full_name}! Your membership is registered. We're excited to have you join us. God bless! - Church Admin"
                if len(full_message) <= 140:
                    message = full_message
                else:
                    # Use shorter template for long names
                    short_message = f"Welcome {member_doc.full_name}! Membership registered. God bless! - Church"
                    if len(short_message) <= 140:
                        message = short_message
                    else:
                        # Truncate name if still too long
                        max_name_length = 140 - len("Welcome ! Membership registered. God bless! - Church")
                        truncated_name = member_doc.full_name[:max_name_length-3] + "..." if len(member_doc.full_name) > max_name_length else member_doc.full_name
                        message = f"Welcome {truncated_name}! Membership registered. God bless! - Church"

                result = sms_api.send_sms([member_doc.contact], message)

                if result["success"]:
                    # Increment SMS usage counter
                    increment_sms_usage(1)
                    # Log the SMS
                    create_sms_log("Bulk Welcome SMS", member_doc.full_name, member_doc.contact, message, "Success")
                    results.append({
                        "member": member_name,
                        "success": True,
                        "phone": member_doc.contact
                    })
                else:
                    create_sms_log("Bulk Welcome SMS", member_doc.full_name, member_doc.contact, message, f"Failed: {result['error']}")
                    results.append({
                        "member": member_name,
                        "success": False,
                        "error": result["error"]
                    })

            except Exception as e:
                results.append({
                    "member": member_name,
                    "success": False,
                    "error": str(e)
                })

        # Summary
        successful = len([r for r in results if r["success"]])
        failed = len([r for r in results if not r["success"]])

        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    except Exception as e:
        frappe.logger().error(f"Bulk welcome SMS error: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def send_bulk_receipt_sms(record_names, **kwargs):
    """Send receipt SMS for multiple tithe/offering records"""
    try:
        if isinstance(record_names, str):
            import json
            record_names = json.loads(record_names)

        # Check SMS access for bulk sending
        sms_count = len(record_names)
        can_send, message = check_sms_access(sms_count, raise_exception=True)

        results = []
        sms_api = SMSAPI()

        for record_name in record_names:
            try:
                # Get tithe/offering record details
                record_doc = frappe.get_doc("Tithes and Offerings", record_name)

                if not record_doc.member:
                    results.append({
                        "record": record_name,
                        "success": False,
                        "error": "No member assigned"
                    })
                    continue

                # Get member details
                member_doc = frappe.get_doc("Member", record_doc.member)

                if not member_doc.contact:
                    results.append({
                        "record": record_name,
                        "success": False,
                        "error": "Member has no phone number"
                    })
                    continue

                # Format amounts
                tithe_formatted = fmt_money(record_doc.tithe_amount) if record_doc.tithe_amount else "0"
                offering_formatted = fmt_money(record_doc.offering_amount) if record_doc.offering_amount else "0"
                total_formatted = fmt_money(record_doc.total_amount)

                # Create receipt message with length check
                date_str = getdate(record_doc.date).strftime('%d/%m/%Y')
                full_message = f"Thank you {member_doc.full_name}! Receipt #{record_doc.receipt_number} {date_str} Total: {total_formatted}. God bless! - Church"

                if len(full_message) <= 140:
                    message = full_message
                else:
                    # Use shorter template
                    short_message = f"Thank you {member_doc.full_name}! Receipt #{record_doc.receipt_number} Total: {total_formatted}. God bless!"
                    if len(short_message) <= 140:
                        message = short_message
                    else:
                        # Truncate name if still too long
                        base_length = len(f"Thank you ! Receipt #{record_doc.receipt_number} Total: {total_formatted}. God bless!")
                        max_name_length = 140 - base_length
                        truncated_name = member_doc.full_name[:max_name_length-3] + "..." if len(member_doc.full_name) > max_name_length else member_doc.full_name
                        message = f"Thank you {truncated_name}! Receipt #{record_doc.receipt_number} Total: {total_formatted}. God bless!"

                result = sms_api.send_sms([member_doc.contact], message)

                if result["success"]:
                    # Increment SMS usage counter
                    increment_sms_usage(1)
                    # Log the SMS
                    create_sms_log("Bulk Receipt SMS", member_doc.full_name, member_doc.contact, message, "Success")
                    results.append({
                        "record": record_name,
                        "success": True,
                        "phone": member_doc.contact,
                        "member": member_doc.full_name
                    })
                else:
                    create_sms_log("Bulk Receipt SMS", member_doc.full_name, member_doc.contact, message, f"Failed: {result['error']}")
                    results.append({
                        "record": record_name,
                        "success": False,
                        "error": result["error"]
                    })

            except Exception as e:
                results.append({
                    "record": record_name,
                    "success": False,
                    "error": str(e)
                })

        # Summary
        successful = len([r for r in results if r["success"]])
        failed = len([r for r in results if not r["success"]])

        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    except Exception as e:
        frappe.logger().error(f"Bulk receipt SMS error: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def test_sms_connection(**kwargs):
    """Test SMS API connection"""
    try:
        sms_api = SMSAPI()
        test_message = "StewardPro SMS test - connection OK"
        test_phone = "255786540517"  # Test phone number

        result = sms_api.send_sms([test_phone], test_message)
        return result

    except Exception as e:
        return {"success": False, "error": str(e)}