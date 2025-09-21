// Copyright (c) 2025, Innocent P Metumba and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tithes and Offerings", {
	refresh(frm) {
		// Add SMS buttons for submitted records with members
		if (frm.doc.docstatus === 1 && frm.doc.member) {
			// Add SMS dropdown group
			frm.add_custom_button(__('Send Receipt SMS'), function() {
				send_receipt_sms_manual(frm);
			}, __('SMS'));

			frm.add_custom_button(__('Test SMS Connection'), function() {
				test_sms_connection_tithe(frm);
			}, __('SMS'));
		}
	}
});

function send_receipt_sms_manual(frm) {
	// Check if member has phone number
	frappe.call({
		method: 'frappe.client.get_value',
		args: {
			doctype: 'Church Member',
			filters: {'name': frm.doc.member},
			fieldname: ['contact', 'full_name']
		},
		callback: function(r) {
			if (r.message && r.message.contact) {
				// Confirm sending SMS
				frappe.confirm(
					__('Send receipt SMS to {0} at {1}?', [r.message.full_name, r.message.contact]),
					function() {
						// Send SMS
						frappe.call({
							method: "stewardpro.stewardpro.api.sms.send_tithe_offering_sms",
							args: {
								member_name: r.message.full_name,
								phone_number: r.message.contact,
								receipt_number: frm.doc.receipt_number,
								tithe_amount: frm.doc.tithe_amount,
								offering_amount: frm.doc.offering_amount,
								total_amount: frm.doc.total_amount,
								date: frm.doc.date
							},
							callback: function(response) {
								if (response.message && response.message.success) {
									frappe.show_alert({
										message: __('Receipt SMS sent successfully to {0}', [r.message.full_name]),
										indicator: 'green'
									});

									frappe.msgprint({
										title: __('SMS Sent'),
										message: __('Receipt SMS has been sent to {0} at {1}', [r.message.full_name, r.message.contact]),
										indicator: 'green'
									});
								} else {
									frappe.show_alert({
										message: __('Failed to send receipt SMS'),
										indicator: 'red'
									});

									frappe.msgprint({
										title: __('SMS Failed'),
										message: __('Failed to send receipt SMS: {0}', [response.message ? response.message.error : 'Unknown error']),
										indicator: 'red'
									});
								}
							},
							error: function() {
								frappe.show_alert({
									message: __('SMS sending error'),
									indicator: 'red'
								});

								frappe.msgprint({
									title: __('SMS Error'),
									message: __('Failed to send receipt SMS. Please check your internet connection and try again.'),
									indicator: 'red'
								});
							}
						});
					}
				);
			} else {
				frappe.msgprint({
					title: __('No Phone Number'),
					message: __('The member {0} does not have a phone number. Please add a phone number to send SMS.', [frm.doc.member]),
					indicator: 'orange'
				});
			}
		},
		error: function() {
			frappe.msgprint({
				title: __('Member Not Found'),
				message: __('Could not find member details. Please check the member assignment.'),
				indicator: 'red'
			});
		}
	});
}

function test_sms_connection_tithe(frm) {
	frappe.show_alert({
		message: __('Testing SMS connection...'),
		indicator: 'blue'
	});

	frappe.call({
		method: "stewardpro.stewardpro.api.sms.test_sms_connection",
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({
					message: __('SMS connection test successful!'),
					indicator: 'green'
				});

				frappe.msgprint({
					title: __('SMS Test Successful'),
					message: __('SMS API connection is working properly. Test message sent successfully.'),
					indicator: 'green'
				});
			} else {
				frappe.show_alert({
					message: __('SMS connection test failed'),
					indicator: 'red'
				});

				frappe.msgprint({
					title: __('SMS Test Failed'),
					message: __('SMS API connection failed: {0}', [r.message ? r.message.error : 'Unknown error']),
					indicator: 'red'
				});
			}
		},
		error: function() {
			frappe.show_alert({
				message: __('SMS test error'),
				indicator: 'red'
			});

			frappe.msgprint({
				title: __('SMS Test Error'),
				message: __('Failed to test SMS connection. Please check your internet connection and try again.'),
				indicator: 'red'
			});
		}
	});
}
