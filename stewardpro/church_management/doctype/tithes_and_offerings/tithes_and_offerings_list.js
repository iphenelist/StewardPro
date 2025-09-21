// Copyright (c) 2025, Innocent P Metumba and contributors
// For license information, please see license.txt

// List View functionality for Tithes and Offerings
frappe.listview_settings['Tithes and Offerings'] = {
	onload: function(listview) {
		// Add bulk SMS button
		listview.page.add_action_item(__('Send Receipt SMS'), function() {
			send_bulk_receipt_sms(listview);
		});
	},

	get_indicator: function(doc) {
		// Add status indicators
		if (doc.docstatus === 1) {
			return [__("Submitted"), "green", "docstatus,=,1"];
		} else if (doc.docstatus === 0) {
			return [__("Draft"), "orange", "docstatus,=,0"];
		} else if (doc.docstatus === 2) {
			return [__("Cancelled"), "red", "docstatus,=,2"];
		}
	}
};

function send_bulk_receipt_sms(listview) {
	// Get selected records
	let selected_records = listview.get_checked_items();
	
	if (selected_records.length === 0) {
		frappe.msgprint({
			title: __('No Records Selected'),
			message: __('Please select tithe/offering records to send receipt SMS.'),
			indicator: 'orange'
		});
		return;
	}
	
	// Filter submitted records only
	let submitted_records = selected_records.filter(record => record.docstatus === 1);
	let non_submitted_records = selected_records.filter(record => record.docstatus !== 1);
	
	if (submitted_records.length === 0) {
		frappe.msgprint({
			title: __('No Submitted Records'),
			message: __('Only submitted tithe/offering records can have receipt SMS sent. Please submit the records first.'),
			indicator: 'orange'
		});
		return;
	}
	
	// Filter records with members who have phone numbers
	let records_with_phone = [];
	let records_without_phone = [];
	let records_without_member = [];
	
	// We need to check each record for member and phone number
	let promises = submitted_records.map(record => {
		return new Promise((resolve) => {
			if (!record.member) {
				records_without_member.push(record);
				resolve();
				return;
			}
			
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Church Member',
					filters: {'name': record.member},
					fieldname: ['contact', 'full_name']
				},
				callback: function(r) {
					if (r.message && r.message.contact) {
						records_with_phone.push({
							...record,
							member_phone: r.message.contact,
							member_name: r.message.full_name
						});
					} else {
						records_without_phone.push(record);
					}
					resolve();
				},
				error: function() {
					records_without_phone.push(record);
					resolve();
				}
			});
		});
	});
	
	Promise.all(promises).then(() => {
		if (records_with_phone.length === 0) {
			let message = __('None of the selected records have members with phone numbers.');
			if (records_without_member.length > 0) {
				message += '<br><br>' + __('<strong>Records without members:</strong> {0}', [records_without_member.length]);
			}
			if (records_without_phone.length > 0) {
				message += '<br><br>' + __('<strong>Members without phone numbers:</strong> {0}', [records_without_phone.length]);
			}
			
			frappe.msgprint({
				title: __('No Phone Numbers'),
				message: message,
				indicator: 'orange'
			});
			return;
		}
		
		// Show confirmation dialog
		let message = __('Send receipt SMS for {0} tithe/offering record(s)?', [records_with_phone.length]);
		
		let skipped_count = records_without_phone.length + records_without_member.length + non_submitted_records.length;
		if (skipped_count > 0) {
			message += '<br><br>' + __('<strong>Note:</strong> {0} record(s) will be skipped:', [skipped_count]);
			if (non_submitted_records.length > 0) {
				message += '<br>• ' + __('Not submitted: {0}', [non_submitted_records.length]);
			}
			if (records_without_member.length > 0) {
				message += '<br>• ' + __('No member assigned: {0}', [records_without_member.length]);
			}
			if (records_without_phone.length > 0) {
				message += '<br>• ' + __('Member has no phone: {0}', [records_without_phone.length]);
			}
		}
		
		frappe.confirm(
			message,
			function() {
				// Show progress alert
				frappe.show_alert({
					message: __('Sending receipt SMS for {0} record(s)...', [records_with_phone.length]),
					indicator: 'blue'
				});
				
				// Extract record names
				let record_names = records_with_phone.map(record => record.name);
				
				// Send bulk SMS
				frappe.call({
					method: "stewardpro.stewardpro.api.sms.send_bulk_receipt_sms",
					args: {
						record_names: record_names
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							let result = r.message;
							
							frappe.show_alert({
								message: __('Receipt SMS sent for {0} record(s), {1} failed', [result.successful, result.failed]),
								indicator: result.failed > 0 ? 'orange' : 'green'
							});
							
							// Show detailed results
							let details_html = `
								<div class="sms-results">
									<h5>Receipt SMS Results</h5>
									<p><strong>Total:</strong> ${result.total}</p>
									<p><strong>Successful:</strong> ${result.successful}</p>
									<p><strong>Failed:</strong> ${result.failed}</p>
							`;
							
							if (result.failed > 0) {
								details_html += '<h6>Failed Records:</h6><ul>';
								result.results.forEach(function(res) {
									if (!res.success) {
										details_html += `<li>${res.record}: ${res.error}</li>`;
									}
								});
								details_html += '</ul>';
							}
							
							details_html += '</div>';
							
							frappe.msgprint({
								title: __('Bulk Receipt SMS Results'),
								message: details_html,
								indicator: result.failed > 0 ? 'orange' : 'green'
							});
							
							// Refresh the list view
							listview.refresh();
						} else {
							frappe.show_alert({
								message: __('Failed to send bulk receipt SMS'),
								indicator: 'red'
							});
							
							frappe.msgprint({
								title: __('SMS Error'),
								message: __('Failed to send bulk receipt SMS: ') + (r.message ? r.message.error : 'Unknown error'),
								indicator: 'red'
							});
						}
					},
					error: function(r) {
						frappe.show_alert({
							message: __('Bulk receipt SMS error'),
							indicator: 'red'
						});
						
						frappe.msgprint({
							title: __('SMS Error'),
							message: __('Failed to send bulk receipt SMS. Please check your internet connection and try again.'),
							indicator: 'red'
						});
					}
				});
			}
		);
	});
}
