// Copyright (c) 2025, Innocent P Metumba and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member", {
	refresh(frm) {
		// Add SMS Test button
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Test SMS Connection'), function() {
				test_sms_connection(frm);
			}, __('SMS'));

			// Add Send Welcome SMS button if member has phone number
			if (frm.doc.contact) {
				frm.add_custom_button(__('Send Welcome SMS'), function() {
					send_welcome_sms_manual(frm);
				}, __('SMS'));
			}
		}
	},
});

function test_sms_connection(frm) {
	frappe.show_alert({
		message: __('Testing SMS connection...'),
		indicator: 'blue'
	});

	frappe.call({
		method: "stewardpro.stewardpro.api.sms.test_sms_connection",
		callback: function(r) {
			if (r.message) {
				if (r.message.success) {
					frappe.show_alert({
						message: __('SMS connection test successful!'),
						indicator: 'green'
					});

					frappe.msgprint({
						title: __('SMS Test Result'),
						message: __('SMS connection is working properly. Test message sent successfully.'),
						indicator: 'green'
					});
				} else {
					frappe.show_alert({
						message: __('SMS connection test failed'),
						indicator: 'red'
					});

					frappe.msgprint({
						title: __('SMS Test Failed'),
						message: __('SMS connection failed: ') + (r.message.error || 'Unknown error'),
						indicator: 'red'
					});
				}
			}
		},
		error: function(r) {
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

function send_welcome_sms_manual(frm) {
	if (!frm.doc.contact) {
		frappe.msgprint({
			title: __('No Phone Number'),
			message: __('Please add a phone number to send SMS.'),
			indicator: 'orange'
		});
		return;
	}

	frappe.confirm(
		__('Send welcome SMS to {0} at {1}?', [frm.doc.full_name, frm.doc.contact]),
		function() {
			frappe.show_alert({
				message: __('Sending welcome SMS...'),
				indicator: 'blue'
			});

			frappe.call({
				method: "stewardpro.stewardpro.api.sms.send_member_registration_sms",
				args: {
					member_name: frm.doc.full_name,
					phone_number: frm.doc.contact
				},
				callback: function(r) {
					if (r.message) {
						if (r.message.success) {
							frappe.show_alert({
								message: __('Welcome SMS sent successfully!'),
								indicator: 'green'
							});

							frappe.msgprint({
								title: __('SMS Sent'),
								message: __('Welcome SMS has been sent to {0} at {1}', [frm.doc.full_name, frm.doc.contact]),
								indicator: 'green'
							});
						} else {
							frappe.show_alert({
								message: __('Failed to send welcome SMS'),
								indicator: 'red'
							});

							frappe.msgprint({
								title: __('SMS Failed'),
								message: __('Failed to send welcome SMS: ') + (r.message.error || 'Unknown error'),
								indicator: 'red'
							});
						}
					}
				},
				error: function(r) {
					frappe.show_alert({
						message: __('SMS sending error'),
						indicator: 'red'
					});

					frappe.msgprint({
						title: __('SMS Error'),
						message: __('Failed to send welcome SMS. Please check your internet connection and try again.'),
						indicator: 'red'
					});
				}
			});
		}
	);
}
