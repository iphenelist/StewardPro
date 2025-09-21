// Copyright (c) 2025, Innocent P Metumba and contributors
// For license information, please see license.txt

// List View functionality for Church Member
frappe.listview_settings['Church Member'] = {
	onload: function(listview) {
		// Add bulk SMS button
		listview.page.add_action_item(__('Send Welcome SMS'), function() {
			send_bulk_welcome_sms(listview);
		});
	},

	get_indicator: function(doc) {
		// Add status indicators
		if (doc.status === "Active") {
			return [__("Active"), "green", "status,=,Active"];
		} else if (doc.status === "Inactive") {
			return [__("Inactive"), "red", "status,=,Inactive"];
		} else if (doc.status === "Transferred") {
			return [__("Transferred"), "orange", "status,=,Transferred"];
		} else if (doc.status === "Deceased") {
			return [__("Deceased"), "darkgrey", "status,=,Deceased"];
		}
	}
};

function send_bulk_welcome_sms(listview) {
	// Get selected members
	let selected_members = listview.get_checked_items();
	
	if (selected_members.length === 0) {
		frappe.msgprint({
			title: __('No Members Selected'),
			message: __('Please select members to send welcome SMS.'),
			indicator: 'orange'
		});
		return;
	}
	
	// Filter members with phone numbers
	let members_with_phone = selected_members.filter(member => member.contact);
	let members_without_phone = selected_members.filter(member => !member.contact);
	
	if (members_with_phone.length === 0) {
		frappe.msgprint({
			title: __('No Phone Numbers'),
			message: __('None of the selected members have phone numbers. Please add phone numbers to send SMS.'),
			indicator: 'orange'
		});
		return;
	}
	
	// Show confirmation dialog
	let message = __('Send welcome SMS to {0} member(s)?', [members_with_phone.length]);
	
	if (members_without_phone.length > 0) {
		message += '<br><br>' + __('<strong>Note:</strong> {0} member(s) will be skipped (no phone number).', [members_without_phone.length]);
	}
	
	frappe.confirm(
		message,
		function() {
			// Show progress alert
			frappe.show_alert({
				message: __('Sending welcome SMS to {0} member(s)...', [members_with_phone.length]),
				indicator: 'blue'
			});
			
			// Extract member names
			let member_names = members_with_phone.map(member => member.name);
			
			// Send bulk SMS
			frappe.call({
				method: "stewardpro.stewardpro.api.sms.send_bulk_welcome_sms",
				args: {
					member_names: member_names
				},
				callback: function(r) {
					if (r.message && r.message.success) {
						let result = r.message;
						
						frappe.show_alert({
							message: __('SMS sent to {0} member(s), {1} failed', [result.successful, result.failed]),
							indicator: result.failed > 0 ? 'orange' : 'green'
						});
						
						// Show detailed results
						let details_html = `
							<div class="sms-results">
								<h5>SMS Sending Results</h5>
								<p><strong>Total:</strong> ${result.total}</p>
								<p><strong>Successful:</strong> ${result.successful}</p>
								<p><strong>Failed:</strong> ${result.failed}</p>
						`;
						
						if (result.failed > 0) {
							details_html += '<h6>Failed Members:</h6><ul>';
							result.results.forEach(function(res) {
								if (!res.success) {
									details_html += `<li>${res.member}: ${res.error}</li>`;
								}
							});
							details_html += '</ul>';
						}
						
						details_html += '</div>';
						
						frappe.msgprint({
							title: __('Bulk SMS Results'),
							message: details_html,
							indicator: result.failed > 0 ? 'orange' : 'green'
						});
						
						// Refresh the list view
						listview.refresh();
					} else {
						frappe.show_alert({
							message: __('Failed to send bulk SMS'),
							indicator: 'red'
						});
						
						frappe.msgprint({
							title: __('SMS Error'),
							message: __('Failed to send bulk SMS: ') + (r.message ? r.message.error : 'Unknown error'),
							indicator: 'red'
						});
					}
				},
				error: function(r) {
					frappe.show_alert({
						message: __('Bulk SMS error'),
						indicator: 'red'
					});
					
					frappe.msgprint({
						title: __('SMS Error'),
						message: __('Failed to send bulk SMS. Please check your internet connection and try again.'),
						indicator: 'red'
					});
				}
			});
		}
	);
}
