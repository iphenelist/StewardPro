// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.query_reports["Annual Report"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": get_year_options(),
			"default": new Date().getFullYear().toString(),
			"reqd": 1
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Format category headers
		if (column.fieldname == "category" && data && data.category.includes("<b>")) {
			return value;
		}
		
		// Format change amounts and percentages
		if (column.fieldname == "change_amount" && data) {
			if (data.change_amount > 0) {
				value = `<span class="text-success">+${value}</span>`;
			} else if (data.change_amount < 0) {
				value = `<span class="text-danger">${value}</span>`;
			}
		}
		
		if (column.fieldname == "change_percentage" && data) {
			if (data.change_percentage > 0) {
				value = `<span class="text-success">+${value}%</span>`;
			} else if (data.change_percentage < 0) {
				value = `<span class="text-danger">${value}%</span>`;
			}
		}
		
		// Highlight net balance
		if (column.fieldname == "amount" && data && data.category.includes("NET BALANCE")) {
			if (data.amount > 0) {
				value = `<span class="text-success"><strong>${value}</strong></span>`;
			} else if (data.amount < 0) {
				value = `<span class="text-danger"><strong>${value}</strong></span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// Initialize chart utilities
		if (typeof stewardpro !== 'undefined' && stewardpro.charts) {
			stewardpro.charts.add_chart_selector(report, get_annual_chart_data, {
				default_chart_type: 'bar',
				height: 350
			});
		}

		// Add chart view buttons
		report.page.add_inner_button(__("Category Breakdown"), function() {
			show_category_breakdown_chart(report);
		}, __("Charts"));

		report.page.add_inner_button(__("Financial Health"), function() {
			show_financial_health_dashboard(report);
		}, __("Charts"));

		// Add custom button to export for conference
		report.page.add_inner_button(__("Export for Conference"), function() {
			let filters = report.get_values();
			frappe.call({
				method: "frappe.desk.query_report.export_query",
				args: {
					report_name: "Annual Report",
					file_format_type: "Excel",
					filters: filters
				},
				callback: function(r) {
					if (r.message) {
						window.open(frappe.urllib.get_full_url(r.message));
					}
				}
			});
		});
		
		// Add button to compare with previous year
		report.page.add_inner_button(__("Year Comparison"), function() {
			let current_year = report.get_values().year;
			let previous_year = parseInt(current_year) - 1;
			
			frappe.msgprint({
				title: __("Year-over-Year Comparison"),
				message: `
					<p>This report shows comparison between ${current_year} and ${previous_year}.</p>
					<p><strong>Key Metrics to Review:</strong></p>
					<ul>
						<li>Total Income Growth/Decline</li>
						<li>Tithe Faithfulness Trends</li>
						<li>Special Offerings Performance</li>
						<li>Expense Management Efficiency</li>
						<li>Net Balance Health</li>
					</ul>
					<p><em>Green values indicate positive growth, red values indicate decline.</em></p>
				`,
				wide: true
			});
		});
		
		// Add button to view detailed breakdown
		report.page.add_inner_button(__("Detailed Breakdown"), function() {
			let year = report.get_values().year;
			
			// Open multiple related reports in new tabs
			frappe.set_route("query-report", "Tithes and Offerings Report", {
				from_date: `${year}-01-01`,
				to_date: `${year}-12-31`
			});
		});
	}
};

function get_year_options() {
	let current_year = new Date().getFullYear();
	let years = [];
	
	for (let i = current_year; i >= current_year - 10; i--) {
		years.push(i.toString());
	}
	
	return years.join('\n');
}

// Chart data processing functions
function get_annual_chart_data(data, filters, chart_type) {
	if (!data || !data.length) return null;

	chart_type = chart_type || 'bar';

	switch (chart_type) {
		case 'pie':
		case 'donut':
			return get_annual_category_breakdown(data);
		case 'line':
		case 'area':
			return get_annual_trend_data(data, true);
		case 'bar':
		default:
			return get_annual_comparison_data(data);
	}
}

function get_annual_comparison_data(data) {
	const categories = [];
	const current_amounts = [];
	const previous_amounts = [];

	data.forEach(row => {
		const category = row.category || "";
		if (category && !category.includes("<b>") && category.trim()) {
			if (category.includes("Tithe") || category.includes("Offering") || category.includes("Income")) {
				categories.push(category);
				current_amounts.push(row.amount || 0);
				previous_amounts.push(row.previous_year_amount || 0);
			}
		}
	});

	return {
		title: __('Year-over-Year Comparison'),
		data: {
			labels: categories,
			datasets: [
				{
					name: __('Current Year'),
					values: current_amounts
				},
				{
					name: __('Previous Year'),
					values: previous_amounts
				}
			]
		}
	};
}

function get_annual_category_breakdown(data) {
	const categories = [];
	const amounts = [];

	data.forEach(row => {
		const category = row.category || "";
		const amount = row.amount || 0;

		if (category && !category.includes("<b>") && category.trim() && amount > 0) {
			if (category.includes("Tithe") || category.includes("Offering")) {
				categories.push(category);
				amounts.push(amount);
			}
		}
	});

	return {
		title: __('Income Categories Breakdown'),
		data: {
			labels: categories,
			datasets: [{
				values: amounts
			}]
		}
	};
}

// Chart view functions
function show_category_breakdown_chart(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for chart'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.annual_report.annual_report.get_category_breakdown_chart',
		args: {
			data: report.data,
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				r.message.title = __('Category Breakdown');
				show_chart_modal(r.message, 'pie');
			}
		}
	});
}

function show_financial_health_dashboard(report) {
	if (!report.data || !report.data.length) {
		frappe.msgprint(__('No data available for dashboard'));
		return;
	}

	frappe.call({
		method: 'stewardpro.stewardpro.report.annual_report.annual_report.get_financial_health_metrics',
		args: {
			data: report.data,
			filters: report.get_values()
		},
		callback: function(r) {
			if (r.message) {
				show_financial_health_modal(r.message, report.get_values().year);
			}
		}
	});
}

function show_financial_health_modal(metrics, year) {
	const dialog = new frappe.ui.Dialog({
		title: __('Financial Health Dashboard - {0}', [year]),
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
						<h3 class="text-success">${frappe.format(metrics.total_income, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Total Income</p>
						<small class="${metrics.income_growth >= 0 ? 'text-success' : 'text-danger'}">
							${metrics.income_growth >= 0 ? '↑' : '↓'} ${Math.abs(metrics.income_growth).toFixed(1)}%
						</small>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-danger">${frappe.format(metrics.total_expenses, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Total Expenses</p>
						<small>${metrics.expense_ratio.toFixed(1)}% of income</small>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="text-warning">${frappe.format(metrics.total_remitted, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Total Remitted</p>
						<small>${metrics.remittance_ratio.toFixed(1)}% of income</small>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card text-center">
					<div class="card-body">
						<h3 class="${metrics.net_income >= 0 ? 'text-success' : 'text-danger'}">${frappe.format(metrics.net_income, {fieldtype: 'Currency'})}</h3>
						<p class="card-text">Net Balance</p>
					</div>
				</div>
			</div>
		</div>
		<div class="row mt-4">
			<div class="col-md-12">
				<div class="card">
					<div class="card-header"><strong>Financial Health Indicators</strong></div>
					<div class="card-body">
						<div class="row">
							<div class="col-md-4">
								<h6>Income Growth</h6>
								<div class="progress">
									<div class="progress-bar ${metrics.income_growth >= 0 ? 'bg-success' : 'bg-danger'}"
										 style="width: ${Math.min(Math.abs(metrics.income_growth), 100)}%">
										${metrics.income_growth.toFixed(1)}%
									</div>
								</div>
							</div>
							<div class="col-md-4">
								<h6>Expense Ratio</h6>
								<div class="progress">
									<div class="progress-bar ${metrics.expense_ratio <= 70 ? 'bg-success' : metrics.expense_ratio <= 85 ? 'bg-warning' : 'bg-danger'}"
										 style="width: ${metrics.expense_ratio}%">
										${metrics.expense_ratio.toFixed(1)}%
									</div>
								</div>
							</div>
							<div class="col-md-4">
								<h6>Remittance Ratio</h6>
								<div class="progress">
									<div class="progress-bar bg-info" style="width: ${metrics.remittance_ratio}%">
										${metrics.remittance_ratio.toFixed(1)}%
									</div>
								</div>
							</div>
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
				colors: stewardpro.charts.color_schemes.church || ['#8BC34A', '#03A9F4', '#FF5722', '#673AB7'],
				...chart_data.options
			});
		} else {
			// Fallback chart configuration
			chart_config = {
				title: chart_data.title,
				data: chart_data.data,
				type: chart_type,
				height: 400,
				colors: ['#8BC34A', '#03A9F4', '#FF5722', '#673AB7', '#E91E63'],
				animate: true,
				...chart_data.options
			};
		}

		new frappe.Chart(dialog.fields_dict.chart_html.$wrapper[0], chart_config);
	}, 100);
}
