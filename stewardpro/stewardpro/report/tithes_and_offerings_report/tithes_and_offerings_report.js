// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Tithes and Offerings Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "member",
			"label": __("Member"),
			"fieldtype": "Link",
			"options": "Member"
		},
		{
			"fieldname": "payment_mode",
			"label": __("Payment Mode"),
			"fieldtype": "Select",
			"options": "\nCash\nMpesa\nBank Transfer\nOther"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "member_name" && data && data.member_name == "Anonymous") {
			value = `<span class="text-muted">${value}</span>`;
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Initialize chart utilities with proper callback
		if (typeof stewardpro !== 'undefined' && stewardpro.charts) {
			stewardpro.charts.add_chart_selector(report, get_tithes_chart_data, {
				default_chart_type: 'bar',
				height: 350
			});
		}

		// Add custom buttons
		report.page.add_inner_button(__("Export Summary"), function() {
			frappe.query_report.export_report();
		});

		// Add chart view buttons
		report.page.add_inner_button(__("Monthly Trends"), function() {
			show_monthly_trends_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Top Contributors"), function() {
			show_member_contributions_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Payment Methods"), function() {
			show_payment_mode_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Summary Dashboard"), function() {
			show_summary_dashboard(report);
		}, __("Charts"));
	},

	"after_datatable_render": function(report) {
		// Auto-refresh chart when data changes
		setTimeout(() => {
			if (report.data && report.data.length > 0 && typeof stewardpro !== 'undefined' && stewardpro.charts) {
				stewardpro.charts.refresh_chart(report, get_tithes_chart_data);
			}
		}, 500);
	}
};

// Chart data processing functions
function get_tithes_chart_data(data, filters, chart_type) {
	if (!data || !data.length) return null;

	chart_type = chart_type || 'bar';

	switch (chart_type) {
		case 'pie':
		case 'donut':
			return get_category_breakdown_data(data);
		case 'line':
		case 'area':
			return get_monthly_trend_data(data, true);
		case 'bar':
		default:
			return get_monthly_trend_data(data, false);
	}
}

function get_monthly_trend_data(data, smooth_line = false) {
	const monthly_data = {};

	data.forEach(row => {
		if (!row.date) return;

		const month = frappe.datetime.str_to_obj(row.date).toISOString().substr(0, 7);
		if (!monthly_data[month]) {
			monthly_data[month] = {
				tithe: 0,
				offering: 0,
				special: 0
			};
		}

		monthly_data[month].tithe += row.tithe_amount || 0;
		monthly_data[month].offering += row.offering_amount || 0;
		monthly_data[month].special += (row.campmeeting_offering || 0) + (row.church_building_offering || 0);
	});

	const months = Object.keys(monthly_data).sort();

	return {
		title: __('Monthly Tithes & Offerings Trends'),
		data: {
			labels: months.map(m => frappe.datetime.str_to_user(m + '-01').substr(0, 7)),
			datasets: [
				{
					name: __('Tithes'),
					values: months.map(m => monthly_data[m].tithe)
				},
				{
					name: __('Offerings'),
					values: months.map(m => monthly_data[m].offering)
				},
				{
					name: __('Special Offerings'),
					values: months.map(m => monthly_data[m].special)
				}
			]
		},
		options: {
			lineOptions: {
				hideDots: smooth_line ? 0 : 1,
				heatline: smooth_line ? 1 : 0
			}
		}
	};
}

function get_category_breakdown_data(data) {
	let total_tithes = 0;
	let total_offerings = 0;
	let total_special = 0;

	data.forEach(row => {
		total_tithes += row.tithe_amount || 0;
		total_offerings += row.offering_amount || 0;
		total_special += (row.campmeeting_offering || 0) + (row.church_building_offering || 0);
	});

	return {
		title: __('Contribution Categories Breakdown'),
		data: {
			labels: [__('Tithes'), __('Regular Offerings'), __('Special Offerings')],
			datasets: [{
				values: [total_tithes, total_offerings, total_special]
			}]
		}
	};
}

// Chart view functions
function show_monthly_trends_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	const chart_data = get_monthly_trend_data(report.data, true);
	show_chart_modal(chart_data, 'line');
}

function show_member_contributions_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	// Get member contribution data
	frappe.call({
		method: 'stewardpro.stewardpro.report.tithes_and_offerings_report.tithes_and_offerings_report.get_member_chart_data',
		args: {
			data: JSON.stringify(report.data),
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Top Contributors');
				show_chart_modal(r.message, 'bar');
			} else {
				frappe.msgprint(__('No contributor data available to display'));
			}
		}
	});
}

function show_payment_mode_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	// Get payment mode data
	frappe.call({
		method: 'stewardpro.stewardpro.report.tithes_and_offerings_report.tithes_and_offerings_report.get_payment_mode_chart_data',
		args: {
			data: JSON.stringify(report.data),
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Payment Methods Distribution');
				show_chart_modal(r.message, 'bar');
			} else {
				frappe.msgprint(__('No payment mode data available to display'));
			}
		}
	});
}

function show_summary_dashboard(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for dashboard'));
		return;
	}

	// Calculate summary statistics
	let total_amount = 0;
	let total_tithes = 0;
	let total_offerings = 0;
	let total_special = 0;
	let unique_members = new Set();
	let payment_modes = {};

	report.data.forEach(row => {
		total_amount += row.total_amount || 0;
		total_tithes += row.tithe_amount || 0;
		total_offerings += row.offering_amount || 0;
		total_special += (row.campmeeting_offering || 0) + (row.church_building_offering || 0);

		if (row.member_name && row.member_name !== 'Anonymous') {
			unique_members.add(row.member_name);
		}

		const mode = row.payment_mode || 'Unknown';
		payment_modes[mode] = (payment_modes[mode] || 0) + (row.total_amount || 0);
	});

	const avg_contribution = unique_members.size > 0 ? total_amount / unique_members.size : 0;
	const most_used_payment = Object.keys(payment_modes).reduce((a, b) =>
		payment_modes[a] > payment_modes[b] ? a : b, 'Cash');

	// Create dashboard dialog
	const dialog = new frappe.ui.Dialog({
		title: __('Tithes & Offerings Dashboard'),
		size: 'extra-large',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'dashboard_html'
			}
		]
	});

	const dashboard_html = `
		<div class="row">
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-success">${frappe.format(total_amount, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Total Collections</p>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-primary">${unique_members.size}</h3>
						<p class="card-text">Contributing Members</p>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-info">${frappe.format(avg_contribution, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Average per Member</p>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-warning">${most_used_payment}</h3>
						<p class="card-text">Top Payment Method</p>
					</div>
				</div>
			</div>
		</div>
		<div class="row mt-4">
			<div class="col-md-4">
				<div class="card">
					<div class="card-header"><strong>Tithes</strong></div>
					<div class="card-body text-center">
						<h4 class="text-success">${frappe.format(total_tithes, {fieldtype: 'Currency'})}</h4>
						<small>${((total_tithes / total_amount) * 100).toFixed(1)}% of total</small>
					</div>
				</div>
			</div>
			<div class="col-md-4">
				<div class="card">
					<div class="card-header"><strong>Regular Offerings</strong></div>
					<div class="card-body text-center">
						<h4 class="text-primary">${frappe.format(total_offerings, {fieldtype: 'Currency'})}</h4>
						<small>${((total_offerings / total_amount) * 100).toFixed(1)}% of total</small>
					</div>
				</div>
			</div>
			<div class="col-md-4">
				<div class="card">
					<div class="card-header"><strong>Special Offerings</strong></div>
					<div class="card-body text-center">
						<h4 class="text-warning">${frappe.format(total_special, {fieldtype: 'Currency'})}</h4>
						<small>${((total_special / total_amount) * 100).toFixed(1)}% of total</small>
					</div>
				</div>
			</div>
		</div>
		<div class="row mt-4">
			<div class="col-md-12">
				<div class="card">
					<div class="card-header"><strong>Payment Methods Breakdown</strong></div>
					<div class="card-body">
						<div class="row">
							${Object.keys(payment_modes).map(mode => `
								<div class="col-md-3 text-center">
									<h5>${frappe.format(payment_modes[mode], {fieldtype: 'Currency'})}</h5>
									<small>${mode}</small>
								</div>
							`).join('')}
						</div>
					</div>
				</div>
			</div>
		</div>
	`;

	dialog.fields_dict.dashboard_html.$wrapper.html(dashboard_html);
	dialog.show();
}

function show_chart_modal(chart_data, chart_type) {
	const dialog = new frappe.ui.Dialog({
		title: chart_data.title || __('Chart'),
		size: 'large',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'chart_html'
			}
		]
	});

	dialog.show();

	setTimeout(() => {
		const chart_config = {
			data: chart_data.data,
			type: chart_type,
			height: 300,
			colors: ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
		};

		new frappe.Chart(dialog.fields_dict.chart_html.$wrapper[0], chart_config);
	}, 200);
}
