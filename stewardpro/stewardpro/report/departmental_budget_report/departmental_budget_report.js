// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Departmental Budget Report"] = {
	"filters": [
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year")
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nSubmitted\nApproved\nActive\nClosed"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "utilization_percentage") {
			if (value > 100) {
				value = `<span class="text-danger"><strong>${value}%</strong></span>`;
			} else if (value > 80) {
				value = `<span class="text-warning">${value}%</span>`;
			} else {
				value = `<span class="text-success">${value}%</span>`;
			}
		}
		
		if (column.fieldname == "status") {
			if (value == "Active") {
				value = `<span class="indicator green">${value}</span>`;
			} else if (value == "Approved") {
				value = `<span class="indicator blue">${value}</span>`;
			} else if (value == "Draft") {
				value = `<span class="indicator orange">${value}</span>`;
			} else if (value == "Closed") {
				value = `<span class="indicator red">${value}</span>`;
			}
		}
		
		if (column.fieldname == "remaining_amount" && data) {
			if (data.remaining_amount < 0) {
				value = `<span class="text-danger">${value}</span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Initialize chart utilities
		if (typeof stewardpro !== 'undefined' && stewardpro.charts) {
			stewardpro.charts.add_chart_selector(report, get_budget_chart_data, {
				default_chart_type: 'bar',
				height: 350
			});
		}

		// Add chart view buttons
		report.page.add_inner_button(__("Budget vs Actual"), function() {
			show_budget_vs_actual_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Utilization Analysis"), function() {
			show_utilization_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Department Comparison"), function() {
			show_department_comparison_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Status Breakdown"), function() {
			show_status_breakdown_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Budget Dashboard"), function() {
			show_budget_dashboard(report);
		}, __("Charts"));

		// Add custom button to show budget summary
		report.page.add_inner_button(__("Budget Summary"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "'stewardpro.stewardpro.report.departmental_budget_report.departmental_budget_report.get_summary_data",
				args: {
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						let data = r.message;
						let overall_utilization = data.total_allocated > 0 ?
							((data.total_spent / data.total_allocated) * 100).toFixed(2) : 0;
						
						frappe.msgprint({
							title: __("Budget Summary"),
							message: `
								<table class="table table-bordered">
									<tr>
										<td><strong>Total Budgets:</strong></td>
										<td>${data.total_budgets || 0}</td>
									</tr>
									<tr>
										<td><strong>Total Allocated:</strong></td>
										<td>${format_currency(data.total_allocated || 0)}</td>
									</tr>
									<tr>
										<td><strong>Total Spent:</strong></td>
										<td>${format_currency(data.total_spent || 0)}</td>
									</tr>
									<tr>
										<td><strong>Total Remaining:</strong></td>
										<td class="${(data.total_remaining || 0) < 0 ? 'text-danger' : 'text-success'}">
											${format_currency(data.total_remaining || 0)}
										</td>
									</tr>
									<tr>
										<td><strong>Overall Utilization:</strong></td>
										<td class="${overall_utilization > 100 ? 'text-danger' : overall_utilization > 80 ? 'text-warning' : 'text-success'}">
											<strong>${overall_utilization}%</strong>
										</td>
									</tr>
								</table>
							`,
							wide: true
						});
					}
				}
			});
		});
		
		// Add button to create new budget
		report.page.add_inner_button(__("New Budget"), function() {
			frappe.new_doc("Department Budget");
		});
	}
};

// Chart data processing functions
function get_budget_chart_data(data, filters, chart_type) {
	if (!data || !data.length) return null;

	chart_type = chart_type || 'bar';

	switch (chart_type) {
		case 'pie':
		case 'donut':
			return get_budget_allocation_breakdown(data);
		case 'line':
		case 'area':
			return get_budget_utilization_trend(data, true);
		case 'bar':
		default:
			return get_budget_vs_actual_data(data);
	}
}

function get_budget_vs_actual_data(data) {
	const departments = [];
	const allocated_amounts = [];
	const actual_amounts = [];

	data.forEach(row => {
		if (row.department_name && row.allocated_amount) {
			departments.push(row.department_name);
			allocated_amounts.push(row.allocated_amount || 0);
			actual_amounts.push(row.actual_expenses || 0);
		}
	});

	return {
		title: __('Budget vs Actual Expenses'),
		data: {
			labels: departments,
			datasets: [
				{
					name: __('Allocated Budget'),
					values: allocated_amounts
				},
				{
					name: __('Actual Expenses'),
					values: actual_amounts
				}
			]
		}
	};
}

function get_budget_allocation_breakdown(data) {
	const departments = [];
	const amounts = [];

	data.forEach(row => {
		if (row.department_name && row.allocated_amount > 0) {
			departments.push(row.department_name);
			amounts.push(row.allocated_amount);
		}
	});

	return {
		title: __('Budget Allocation by Department'),
		data: {
			labels: departments,
			datasets: [{
				values: amounts
			}]
		}
	};
}

// Chart view functions
function show_budget_vs_actual_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	const chart_data = get_budget_vs_actual_data(report.data);
	show_chart_modal(chart_data, 'bar');
}

function show_utilization_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.departmental_budget_report.departmental_budget_report.get_utilization_chart_data',
		args: {
			data: report.data,
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Budget Utilization Analysis');
				show_chart_modal(r.message, 'bar');
			}
		}
	});
}

function show_department_comparison_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.departmental_budget_report.departmental_budget_report.get_department_comparison_chart',
		args: {
			data: report.data,
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Department Budget Comparison');
				show_chart_modal(r.message, 'pie');
			}
		}
	});
}

function show_status_breakdown_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.departmental_budget_report.departmental_budget_report.get_budget_status_breakdown',
		args: {
			data: report.data,
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Budget Status Breakdown');
				show_chart_modal(r.message, 'donut');
			}
		}
	});
}

function show_budget_dashboard(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for dashboard'));
		return;
	}

	// Calculate dashboard metrics
	let total_allocated = 0;
	let total_spent = 0;
	let over_budget_count = 0;
	let under_utilized_count = 0;
	let departments_count = report.data.length;

	report.data.forEach(row => {
		total_allocated += row.allocated_amount || 0;
		total_spent += row.actual_expenses || 0;

		const utilization = row.utilization_percentage || 0;
		if (utilization > 100) {
			over_budget_count++;
		} else if (utilization < 50) {
			under_utilized_count++;
		}
	});

	const overall_utilization = total_allocated > 0 ? (total_spent / total_allocated * 100) : 0;
	const remaining_budget = total_allocated - total_spent;

	// Create dashboard dialog
	const dialog = new frappe.ui.Dialog({
		title: __('Budget Dashboard'),
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
						<h3 class="text-primary">${frappe.format(total_allocated, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Total Allocated</p>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-danger">${frappe.format(total_spent, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Total Spent</p>
						<small>${overall_utilization.toFixed(1)}% utilized</small>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="${remaining_budget >= 0 ? 'text-success' : 'text-danger'}">${frappe.format(remaining_budget, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Remaining Budget</p>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-info">${departments_count}</h3>
						<p class="card-text">Total Departments</p>
					</div>
				</div>
			</div>
		</div>
		<div class="row mt-4">
			<div class="col-md-4">
				<div class="card">
					<div class="card-header"><strong>Over Budget</strong></div>
					<div class="card-body text-center">
						<h4 class="text-danger">${over_budget_count}</h4>
						<small>${departments_count > 0 ? (over_budget_count / departments_count * 100).toFixed(1) : 0}% of departments</small>
					</div>
				</div>
			</div>
			<div class="col-md-4">
				<div class="card">
					<div class="card-header"><strong>Under Utilized</strong></div>
					<div class="card-body text-center">
						<h4 class="text-warning">${under_utilized_count}</h4>
						<small>${departments_count > 0 ? (under_utilized_count / departments_count * 100).toFixed(1) : 0}% of departments</small>
					</div>
				</div>
			</div>
			<div class="col-md-4">
				<div class="card">
					<div class="card-header"><strong>Overall Utilization</strong></div>
					<div class="card-body text-center">
						<div class="progress mb-2">
							<div class="progress-bar ${overall_utilization <= 100 ? 'bg-success' : 'bg-danger'}"
								 style="width: ${Math.min(overall_utilization, 100)}%">
								${overall_utilization.toFixed(1)}%
							</div>
						</div>
						<h4 class="${overall_utilization <= 100 ? 'text-success' : 'text-danger'}">${overall_utilization.toFixed(1)}%</h4>
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
		size: 'extra-large',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'chart_html'
			}
		]
	});

	dialog.show();

	setTimeout(() => {
		let chart_config;
		if (typeof stewardpro !== 'undefined' && stewardpro.charts && stewardpro.charts.create_chart_config) {
			chart_config = stewardpro.charts.create_chart_config(chart_data.data, {
				title: chart_data.title,
				type: chart_type,
				height: 400,
				colors: stewardpro.charts.color_schemes.default || ['#36A2EB', '#FF6384', '#4BC0C0', '#FF9F40'],
				...chart_data.options
			});
		} else {
			// Fallback chart configuration
			chart_config = {
				title: chart_data.title,
				data: chart_data.data,
				type: chart_type,
				height: 400,
				colors: ['#36A2EB', '#FF6384', '#4BC0C0', '#FF9F40', '#9966FF'],
				animate: true,
				...chart_data.options
			};
		}

		new frappe.Chart(dialog.fields_dict.chart_html.$wrapper[0], chart_config);
	}, 100);
}

function get_budget_utilization_trend(data, smooth = false) {
	if (!data || !data.length) return null;

	let departments = [];
	let utilization_rates = [];

	data.forEach(row => {
		if (row.department_name && row.utilization_percentage !== undefined) {
			departments.push(row.department_name);
			utilization_rates.push(row.utilization_percentage);
		}
	});

	return {
		title: 'Budget Utilization Trend',
		data: {
			labels: departments,
			datasets: [{
				name: 'Utilization %',
				values: utilization_rates
			}]
		},
		type: smooth ? 'area' : 'line',
		height: 300,
		colors: ['#2196F3']
	};
}
