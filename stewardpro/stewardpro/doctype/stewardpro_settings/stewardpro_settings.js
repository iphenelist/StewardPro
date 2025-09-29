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

		frm.add_custom_button(__('Upgrade Package'), function() {
			show_upgrade_dialog(frm);
		}, __('Actions'));

		// Set field properties based on subscription status
		set_field_properties(frm);
		
		// Show subscription status indicator
		show_subscription_status(frm);
		
		// Update member count
		update_member_count(frm);
	},

	subscription_package: function(frm) {
		// Update package-specific settings when package changes
		update_package_settings(frm);
	},

	enable_sms_integration: function(frm) {
		// Toggle SMS fields visibility
		toggle_sms_fields(frm);
		validate_sms_access(frm);
	},

	enable_mobile_money_integration: function(frm) {
		// Toggle mobile money fields visibility
		toggle_mobile_money_fields(frm);
		validate_mobile_money_access(frm);
	},

	subscription_status: function(frm) {
		set_field_properties(frm);
	}
});

function set_field_properties(frm) {
	const is_expired_or_suspended = ['Expired', 'Suspended'].includes(frm.doc.subscription_status);
	
	// Disable premium features for expired/suspended subscriptions
	if (is_expired_or_suspended) {
		frm.set_value('enable_sms_integration', 0);
		frm.set_value('enable_mobile_money_integration', 0);
		frm.set_value('enable_advanced_analytics', 0);
		frm.set_value('enable_multi_branch', 0);
		frm.set_value('enable_api_access', 0);
		frm.set_value('enable_custom_reports', 0);
		frm.set_value('enable_white_label', 0);
		
		// Make premium feature fields read-only
		const premium_fields = [
			'enable_sms_integration', 'enable_mobile_money_integration',
			'enable_advanced_analytics', 'enable_multi_branch',
			'enable_api_access', 'enable_custom_reports', 'enable_white_label'
		];
		
		premium_fields.forEach(field => {
			frm.set_df_property(field, 'read_only', 1);
		});
	} else {
		// Enable fields for active subscriptions
		const premium_fields = [
			'enable_sms_integration', 'enable_mobile_money_integration',
			'enable_advanced_analytics', 'enable_multi_branch',
			'enable_api_access', 'enable_custom_reports', 'enable_white_label'
		];
		
		premium_fields.forEach(field => {
			frm.set_df_property(field, 'read_only', 0);
		});
	}
}

function show_subscription_status(frm) {
	const status = frm.doc.subscription_status;
	const end_date = frm.doc.subscription_end_date;
	
	let indicator_color = 'green';
	let message = '';
	
	switch(status) {
		case 'Active':
			indicator_color = 'green';
			message = `Active until ${frappe.datetime.str_to_user(end_date)}`;
			break;
		case 'Trial':
			indicator_color = 'orange';
			message = `Trial expires on ${frappe.datetime.str_to_user(end_date)}`;
			break;
		case 'Expired':
			indicator_color = 'red';
			message = `Expired on ${frappe.datetime.str_to_user(end_date)}`;
			break;
		case 'Suspended':
			indicator_color = 'red';
			message = 'Subscription suspended';
			break;
	}
	
	frm.dashboard.add_indicator(__('Subscription Status: {0}', [message]), indicator_color);
}

function update_package_settings(frm) {
	// This will trigger the server-side validation to update package defaults
	frm.save();
}

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

function validate_sms_access(frm) {
	if (frm.doc.enable_sms_integration) {
		const package_name = frm.doc.subscription_package;
		if (['Starter', 'Professional'].includes(package_name)) {
			frappe.msgprint({
				title: __('SMS Integration'),
				message: __('SMS Integration is not included in {0} package. Please upgrade to Premium or Enterprise, or purchase SMS add-on.', [package_name]),
				indicator: 'orange'
			});
		}
	}
}

function validate_mobile_money_access(frm) {
	if (frm.doc.enable_mobile_money_integration) {
		const package_name = frm.doc.subscription_package;
		if (['Starter', 'Professional'].includes(package_name)) {
			frappe.msgprint({
				title: __('Mobile Money Integration'),
				message: __('Mobile Money Integration is not included in {0} package. Please upgrade to Premium or Enterprise, or purchase Mobile Money add-on.', [package_name]),
				indicator: 'orange'
			});
		}
	}
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

function show_upgrade_dialog(frm) {
	const packages = [
		{name: 'Starter', cost: 'TZS 3,000,000/month'},
		{name: 'Professional', cost: 'TZS 5,500,000/month'},
		{name: 'Premium', cost: 'TZS 8,500,000/month'},
		{name: 'Enterprise', cost: 'TZS 15,000,000/month'}
	];
	
	let package_html = '<div class="row">';
	packages.forEach(pkg => {
		const is_current = pkg.name === frm.doc.subscription_package;
		const badge = is_current ? '<span class="badge badge-success">Current</span>' : '';
		
		package_html += `
			<div class="col-md-6 mb-3">
				<div class="card">
					<div class="card-body">
						<h6 class="card-title">${pkg.name} ${badge}</h6>
						<p class="card-text">${pkg.cost}</p>
						${!is_current ? `<button class="btn btn-sm btn-primary" onclick="upgrade_to_package('${pkg.name}')">Upgrade</button>` : ''}
					</div>
				</div>
			</div>
		`;
	});
	package_html += '</div>';
	
	frappe.msgprint({
		title: __('Upgrade Package'),
		message: package_html,
		wide: true
	});
}

window.upgrade_to_package = function(package_name) {
	frappe.confirm(
		__('Are you sure you want to upgrade to {0} package?', [package_name]),
		function() {
			frappe.call({
				method: 'frappe.client.set_value',
				args: {
					doctype: 'StewardPro Settings',
					name: 'StewardPro Settings',
					fieldname: 'subscription_package',
					value: package_name
				},
				callback: function() {
					frappe.msgprint(__('Package upgraded successfully'));
					cur_frm.reload_doc();
				}
			});
		}
	);
};
