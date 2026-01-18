// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Financial Summary"] = {
	"filters": [
		{
			"fieldname": "period",
			"label": __("Period"),
			"fieldtype": "Select",
			"options": "Current Month\nQuarter\nYear to Date\nCustom",
			"default": "Current Month"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Format headers
		if (column.fieldname == "category" && data && data.category) {
			if (data.category.includes("<b>")) {
				value = data.category;
			}
		}
		
		// Color code percentage changes
		if (column.fieldname == "month_change" || column.fieldname == "year_change") {
			if (data && typeof data[column.fieldname] === 'number') {
				const change = data[column.fieldname];
				if (change > 0) {
					value = `<span class="text-success">${value}</span>`;
				} else if (change < 0) {
					value = `<span class="text-danger">${value}</span>`;
				}
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Initialize chart utilities
		if (typeof stewardpro !== 'undefined' && stewardpro.charts) {
			stewardpro.charts.add_chart_selector(report, get_financial_chart_data, {
				default_chart_type: 'pie',
				height: 350
			});
		}

		// Add custom chart buttons
		report.page.add_inner_button(__("Income vs Expenses"), function() {
			show_income_expense_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Income Breakdown"), function() {
			show_income_breakdown_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Expense Analysis"), function() {
			show_expense_breakdown_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Trend Comparison"), function() {
			show_trend_comparison_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Financial Dashboard"), function() {
			show_financial_dashboard(report);
		}, __("Charts"));

		// Add export button
		report.page.add_inner_button(__("Export Summary"), function() {
			frappe.query_report.export_report();
		});
	},

	"after_datatable_render": function(report) {
		// Auto-refresh chart when data changes
		setTimeout(() => {
			if (report.data && report.data.length > 0 && typeof stewardpro !== 'undefined' && stewardpro.charts) {
				stewardpro.charts.refresh_chart(report, get_financial_chart_data);
			}
		}, 500);
	}
};

// Chart data processing functions
function get_financial_chart_data(data, filters, chart_type) {
	if (!data || !data.length) return null;

	chart_type = chart_type || 'pie';

	switch (chart_type) {
		case 'pie':
		case 'donut':
			return get_income_expense_pie_data(data);
		case 'line':
		case 'area':
			return get_financial_trend_data(data, true);
		case 'bar':
		default:
			return get_financial_trend_data(data, false);
	}
}

function get_income_expense_pie_data(data) {
	let total_income = 0;
	let total_expenses = 0;

	data.forEach(row => {
		const category = row.category || "";
		const current_month = row.current_month || 0;

		if (category === "Tithes" || category === "Regular Offerings" || category === "Special Offerings") {
			total_income += current_month;
		} else if (category.includes("Expenses")) {
			total_expenses += current_month;
		}
	});

	return {
		title: __('Income vs Expenses (Current Month)'),
		data: {
			labels: [__('Income'), __('Expenses')],
			datasets: [{
				values: [total_income, total_expenses]
			}]
		}
	};
}

function get_financial_trend_data(data, smooth_line = false) {
	const income_categories = [];
	const current_month_values = [];
	const previous_month_values = [];
	const ytd_values = [];
	
	data.forEach(row => {
		const category = row.category || "";
		if (category === "Tithes" || category === "Regular Offerings" || category === "Special Offerings") {
			income_categories.push(category);
			current_month_values.push(row.current_month || 0);
			previous_month_values.push(row.previous_month || 0);
			ytd_values.push(row.year_to_date || 0);
		}
	});
	
	return {
		title: __('Financial Trends Comparison'),
		data: {
			labels: income_categories,
			datasets: [
				{
					name: __('Current Month'),
					values: current_month_values
				},
				{
					name: __('Previous Month'),
					values: previous_month_values
				},
				{
					name: __('Year to Date'),
					values: ytd_values
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

// Chart view functions
function show_income_expense_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}
	
	const chart_data = get_income_expense_pie_data(report.data);
	show_chart_modal(chart_data, 'pie');
}

function show_income_breakdown_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.financial_summary.financial_summary.get_income_breakdown_chart',
		args: {
			data: JSON.stringify(report.data),
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Income Breakdown');
				show_chart_modal(r.message, 'donut');
			} else {
				frappe.msgprint(__('No income data available to display'));
			}
		}
	});
}

function show_expense_breakdown_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.financial_summary.financial_summary.get_expense_breakdown_chart',
		args: {
			data: JSON.stringify(report.data),
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Expense Analysis');
				show_chart_modal(r.message, 'bar');
			} else {
				frappe.msgprint(__('No expense data available to display'));
			}
		}
	});
}

function show_trend_comparison_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.financial_summary.financial_summary.get_trend_comparison_chart',
		args: {
			data: JSON.stringify(report.data),
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Trend Comparison');
				show_chart_modal(r.message, 'bar');
			} else {
				frappe.msgprint(__('No trend data available to display'));
			}
		}
	});
}

function show_financial_dashboard(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for dashboard'));
		return;
	}
	
	// Calculate financial metrics
	let total_income_current = 0;
	let total_income_previous = 0;
	let total_income_ytd = 0;
	let total_expenses_current = 0;
	let total_expenses_ytd = 0;
	
	report.data.forEach(row => {
		const category = row.category || "";
		const current = row.current_month || 0;
		const previous = row.previous_month || 0;
		const ytd = row.year_to_date || 0;

		if (category === "Tithes" || category === "Regular Offerings" || category === "Special Offerings") {
			total_income_current += current;
			total_income_previous += previous;
			total_income_ytd += ytd;
		} else if (category.includes("Expenses")) {
			total_expenses_current += current;
			total_expenses_ytd += ytd;
		}
	});
	
	const net_current = total_income_current - total_expenses_current;
	const net_ytd = total_income_ytd - total_expenses_ytd;
	const income_growth = total_income_previous > 0 ? 
		((total_income_current - total_income_previous) / total_income_previous * 100) : 0;
	
	// Create dashboard dialog
	const dialog = new frappe.ui.Dialog({
		title: __('Financial Dashboard'),
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
						<h3 class="text-success">${frappe.format(total_income_current, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Current Month Income</p>
						<small class="${income_growth >= 0 ? 'text-success' : 'text-danger'}">
							${income_growth >= 0 ? '↑' : '↓'} ${Math.abs(income_growth).toFixed(1)}%
						</small>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-danger">${frappe.format(total_expenses_current, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Current Month Expenses</p>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="${net_current >= 0 ? 'text-success' : 'text-danger'}">${frappe.format(net_current, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Net Current Month</p>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="${net_ytd >= 0 ? 'text-success' : 'text-danger'}">${frappe.format(net_ytd, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Net Year to Date</p>
					</div>
				</div>
			</div>
		</div>
		<div class="row mt-4">
			<div class="col-md-6">
				<div class="card">
					<div class="card-header"><strong>Income Summary (YTD)</strong></div>
					<div class="card-body">
						<div class="progress mb-2">
							<div class="progress-bar bg-success" style="width: 100%"></div>
						</div>
						<h4 class="text-success">${frappe.format(total_income_ytd, {fieldtype: 'Currency'})}</h4>
					</div>
				</div>
			</div>
			<div class="col-md-6">
				<div class="card">
					<div class="card-header"><strong>Expenses Summary (YTD)</strong></div>
					<div class="card-body">
						<div class="progress mb-2">
							<div class="progress-bar bg-danger" style="width: ${total_income_ytd > 0 ? (total_expenses_ytd / total_income_ytd * 100) : 0}%"></div>
						</div>
						<h4 class="text-danger">${frappe.format(total_expenses_ytd, {fieldtype: 'Currency'})}</h4>
						<small>${total_income_ytd > 0 ? (total_expenses_ytd / total_income_ytd * 100).toFixed(1) : 0}% of income</small>
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
