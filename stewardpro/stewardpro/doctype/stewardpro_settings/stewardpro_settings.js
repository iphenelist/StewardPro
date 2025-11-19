// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('StewardPro Settings', {
	refresh: function(frm) {
		// Add custom buttons
		frm.add_custom_button(__('Test SMS Connection'), function() {
			test_sms_connection(frm);
		}, __('Actions'));

		frm.add_custom_button(__('Test Mobile Money'), function() {
			test_mobile_money_connection(frm);
		}, __('Actions'));
	},

	enable_sms_integration: function(frm) {
		// Toggle SMS fields visibility
		toggle_sms_fields(frm);
	},

	enable_mobile_money_integration: function(frm) {
		// Toggle mobile money fields visibility
		toggle_mobile_money_fields(frm);
	}
});



function toggle_sms_fields(frm) {
	const show_fields = frm.doc.enable_sms_integration;

	const sms_fields = [
		'sms_api_key', 'sms_api_secret', 'sms_sender_id'
	];

	sms_fields.forEach(field => {
		frm.toggle_display(field, show_fields);
	});
}

function toggle_mobile_money_fields(frm) {
	const show_fields = frm.doc.enable_mobile_money_integration;

	const mm_fields = [
		'mobile_money_base_url', 'supported_providers', 'money_api_key', 'money_public_key'
	];

	mm_fields.forEach(field => {
		frm.toggle_display(field, show_fields);
	});
}


function test_sms_connection(frm) {
	if (!frm.doc.enable_sms_integration) {
		frappe.msgprint(__('SMS Integration is not enabled'));
		return;
	}
	
	frappe.call({
		method: 'stewardpro.stewardpro.api.sms.test_sms_connection',
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.msgprint({
					title: __('SMS Test Successful'),
					message: __('SMS connection is working properly'),
					indicator: 'green'
				});
			} else {
				frappe.msgprint({
					title: __('SMS Test Failed'),
					message: r.message ? r.message.error : __('Unknown error occurred'),
					indicator: 'red'
				});
			}
		}
	});
}

function test_mobile_money_connection(frm) {
	if (!frm.doc.enable_mobile_money_integration) {
		frappe.msgprint(__('Mobile Money Integration is not enabled'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.api.money.test_mobile_money_connection',
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.msgprint({
					title: __('Mobile Money Test'),
					message: __('Mobile Money connection test successful!'),
					indicator: 'green'
				});
			} else {
				frappe.msgprint({
					title: __('Mobile Money Test'),
					message: __('Mobile Money connection test failed: ' + (r.message?.error || 'Unknown error')),
					indicator: 'red'
				});
			}
		},
		error: function(r) {
			frappe.msgprint({
				title: __('Mobile Money Test'),
				message: __('Error testing Mobile Money connection'),
				indicator: 'red'
			});
		}
	});
}




