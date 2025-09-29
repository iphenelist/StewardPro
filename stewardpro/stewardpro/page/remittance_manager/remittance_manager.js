frappe.pages['remittance-manager'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Remittance Manager',
		single_column: true
	});

	// Load the HTML content
	$(frappe.render_template("remittance_manager", {})).appendTo(page.body);
	
	// Initialize the page
	new RemittanceManager(page);
};

class RemittanceManager {
	constructor(page) {
		this.page = page;
		this.setup_events();
		this.load_recent_remittances();
	}

	setup_events() {
		// Preview button click
		$('#preview-btn').on('click', () => {
			this.preview_remittance();
		});

		// Create button click
		$('#create-btn').on('click', () => {
			this.create_remittance();
		});

		// Auto-preview when dates change
		$('#period_start, #period_end').on('change', () => {
			if ($('#period_start').val() && $('#period_end').val()) {
				this.preview_remittance();
			}
		});
	}

	preview_remittance() {
		const period_start = $('#period_start').val();
		const period_end = $('#period_end').val();

		if (!period_start || !period_end) {
			frappe.msgprint('Please select both start and end dates');
			return;
		}

		if (new Date(period_start) > new Date(period_end)) {
			frappe.msgprint('Start date cannot be after end date');
			return;
		}

		$('#preview-content').html('<p class="text-muted">Loading preview...</p>');

		frappe.call({
			method: 'stewardpro.stewardpro.tasks.get_remittance_preview',
			args: {
				period_start: period_start,
				period_end: period_end
			},
			callback: (r) => {
				if (r.message) {
					this.render_preview(r.message);
				}
			}
		});
	}

	render_preview(data) {
		if (data.message) {
			$('#preview-content').html(`<p class="text-warning">${data.message}</p>`);
			return;
		}

		const html = `
			<div class="preview-data">
				<h5>Period: ${frappe.datetime.str_to_user(data.period_start)} to ${frappe.datetime.str_to_user(data.period_end)}</h5>
				<table class="table table-sm">
					<tr>
						<td><strong>Total Tithe:</strong></td>
						<td class="text-right">${format_currency(data.total_tithe)}</td>
					</tr>
					<tr>
						<td><strong>Offering to Field (58%):</strong></td>
						<td class="text-right">${format_currency(data.total_offering_to_field)}</td>
					</tr>
					<tr>
						<td><strong>Special Offerings:</strong></td>
						<td class="text-right">${format_currency(data.total_special_offerings)}</td>
					</tr>
					<tr class="table-info">
						<td><strong>Total Remittance:</strong></td>
						<td class="text-right"><strong>${format_currency(data.total_remittance)}</strong></td>
					</tr>
					<tr>
						<td><strong>Total Records:</strong></td>
						<td class="text-right">${data.total_records}</td>
					</tr>
				</table>
			</div>
		`;

		$('#preview-content').html(html);
	}

	create_remittance() {
		const period_start = $('#period_start').val();
		const period_end = $('#period_end').val();
		const remittance_period = $('#remittance_period').val();

		if (!period_start || !period_end) {
			frappe.msgprint('Please select both start and end dates');
			return;
		}

		if (new Date(period_start) > new Date(period_end)) {
			frappe.msgprint('Start date cannot be after end date');
			return;
		}

		frappe.confirm(
			`Create remittance for period ${frappe.datetime.str_to_user(period_start)} to ${frappe.datetime.str_to_user(period_end)}?`,
			() => {
				frappe.call({
					method: 'stewardpro.stewardpro.tasks.create_manual_remittance',
					args: {
						period_start: period_start,
						period_end: period_end,
						remittance_period: remittance_period
					},
					callback: (r) => {
						if (r.message) {
							frappe.msgprint(`Remittance ${r.message} created successfully`);
							this.load_recent_remittances();
							
							// Open the created remittance
							frappe.set_route('Form', 'Remittance', r.message);
						}
					}
				});
			}
		);
	}

	load_recent_remittances() {
		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Remittance',
				fields: ['name', 'remittance_date', 'organization_name', 'total_remittance_amount', 'status'],
				order_by: 'creation desc',
				limit: 10
			},
			callback: (r) => {
				if (r.message) {
					this.render_recent_remittances(r.message);
				}
			}
		});
	}

	render_recent_remittances(remittances) {
		if (!remittances || remittances.length === 0) {
			$('#recent-remittances').html('<p class="text-muted">No remittances found</p>');
			return;
		}

		let html = `
			<table class="table table-striped">
				<thead>
					<tr>
						<th>Remittance</th>
						<th>Date</th>
						<th>Organization</th>
						<th>Amount</th>
						<th>Status</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
		`;

		remittances.forEach(remittance => {
			html += `
				<tr>
					<td><a href="/app/remittance/${remittance.name}">${remittance.name}</a></td>
					<td>${frappe.datetime.str_to_user(remittance.remittance_date)}</td>
					<td>${remittance.organization_name}</td>
					<td class="text-right">${format_currency(remittance.total_remittance_amount)}</td>
					<td><span class="badge badge-${this.get_status_color(remittance.status)}">${remittance.status}</span></td>
					<td>
						<a href="/app/remittance/${remittance.name}" class="btn btn-sm btn-outline-primary">View</a>
					</td>
				</tr>
			`;
		});

		html += '</tbody></table>';
		$('#recent-remittances').html(html);
	}

	get_status_color(status) {
		const colors = {
			'Draft': 'secondary',
			'Pending Approval': 'warning',
			'Approved': 'info',
			'Sent': 'primary',
			'Received': 'success'
		};
		return colors[status] || 'secondary';
	}
}

// Helper function to format currency
function format_currency(amount) {
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: frappe.defaults.get_default('currency') || 'USD'
	}).format(amount || 0);
}
