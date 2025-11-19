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

		frm.add_custom_button(__('Check Usage'), function() {
			show_usage_dashboard(frm);
		}, __('Actions'));

		// Update member count
		update_member_count(frm);
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
		'sms_monthly_quota', 'sms_cost_per_message', 'sms_provider',
		'sms_api_key', 'sms_api_secret', 'sms_sender_id'
	];
	
	sms_fields.forEach(field => {
		frm.toggle_display(field, show_fields);
	});
}

function toggle_mobile_money_fields(frm) {
	const show_fields = frm.doc.enable_mobile_money_integration;
	
	const mm_fields = [
		'supported_providers', 'mobile_money_transaction_fee',
		'mpesa_api_key', 'mpesa_public_key', 'tigo_pesa_api_key', 'airtel_money_api_key'
	];
	
	mm_fields.forEach(field => {
		frm.toggle_display(field, show_fields);
	});
}



function update_member_count(frm) {
	frappe.call({
		method: 'frappe.client.get_count',
		args: {
			doctype: 'Member',
			filters: {'status': "Active"}
		},
		callback: function(r) {
			if (r.message) {
				frm.set_value('current_member_count', r.message);
			}
		}
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
	
	frappe.msgprint({
		title: __('Mobile Money Test'),
		message: __('Mobile Money connection test is not yet implemented'),
		indicator: 'blue'
	});
}

function show_usage_dashboard(frm) {
	frappe.call({
		method: 'stewardpro.stewardpro.doctype.stewardpro_settings.stewardpro_settings.get_sms_status',
		callback: function(r) {
			if (r.message) {
				const sms_data = r.message;
				let usage_html = `
					<div class="row">
						<div class="col-md-6">
							<h5>SMS Usage</h5>
							<p><strong>Quota:</strong> ${sms_data.quota}</p>
							<p><strong>Used:</strong> ${sms_data.used}</p>
							<p><strong>Balance:</strong> ${sms_data.balance}</p>
							<p><strong>Status:</strong> ${sms_data.can_send ? 'Available' : 'Quota Exceeded'}</p>
						</div>
						<div class="col-md-6">
							<h5>Member Count</h5>
							<p><strong>Current:</strong> ${frm.doc.current_member_count}</p>
							<p><strong>Limit:</strong> ${frm.doc.max_members === -1 ? 'Unlimited' : frm.doc.max_members}</p>
						</div>
					</div>
				`;
				
				frappe.msgprint({
					title: __('Usage Dashboard'),
					message: usage_html,
					wide: true
				});
			}
		}
	});
}


