// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

/**
 * StewardPro Chart Utilities
 * Provides common chart functionality for all reports
 */

frappe.provide('stewardpro.charts');

stewardpro.charts = {
    // Chart type options
    chart_types: [
        { value: 'bar', label: __('Bar Chart') },
        { value: 'line', label: __('Line Chart') },
        { value: 'pie', label: __('Pie Chart') },
        { value: 'donut', label: __('Donut Chart') },
        { value: 'area', label: __('Area Chart') }
    ],

    // Color schemes
    color_schemes: {
        default: ['#36A2EB', '#FF6384', '#4BC0C0', '#FF9F40', '#9966FF', '#FFCD56', '#FF6384', '#C9CBCF'],
        stewardpro: ['#2E7D32', '#1976D2', '#F57C00', '#7B1FA2', '#D32F2F', '#388E3C', '#1565C0', '#F9A825'],
        financial: ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#009688', '#3F51B5', '#FFC107'],
        church: ['#8BC34A', '#03A9F4', '#FF5722', '#673AB7', '#E91E63', '#00BCD4', '#3F51B5', '#CDDC39']
    },

    /**
     * Create chart configuration with type selection
     */
    create_chart_config: function(data, options = {}) {
        const default_options = {
            title: '',
            type: 'bar',
            height: 300,
            colors: this.color_schemes.stewardpro,
            animate: true,
            truncateLegends: true,
            maxLegendPoints: 6,
            lineOptions: {
                hideDots: 0,
                heatline: 1,
                regionFill: 1
            },
            axisOptions: {
                xAxisMode: 'tick',
                yAxisMode: 'tick',
                xIsSeries: 0
            },
            tooltipOptions: {
                formatTooltipX: d => (d + '').toUpperCase(),
                formatTooltipY: d => frappe.format(d, { fieldtype: 'Currency' })
            }
        };

        return Object.assign(default_options, options, { data: data });
    },

    /**
     * Add chart type selector to report
     */
    add_chart_selector: function(report, chart_data_callback, options = {}) {
        if (!report.page) return;

        // Add chart type selector
        const chart_type_field = report.page.add_field({
            fieldname: 'chart_type',
            fieldtype: 'Select',
            label: __('Chart Type'),
            options: this.chart_types.map(t => t.value).join('\n'),
            default: options.default_chart_type || 'bar',
            change: () => {
                this.refresh_chart(report, chart_data_callback, options);
            }
        });

        // Add chart toggle button
        report.page.add_inner_button(__('Toggle Chart'), () => {
            this.toggle_chart_visibility(report);
        }, __('Chart'));

        // Add export chart button
        report.page.add_inner_button(__('Export Chart'), () => {
            this.export_chart(report);
        }, __('Chart'));

        // Store chart utilities in report object
        report.chart_utils = {
            chart_type_field: chart_type_field,
            chart_data_callback: chart_data_callback,
            options: options
        };

        return chart_type_field;
    },

    /**
     * Refresh chart based on current data and selected type
     */
    refresh_chart: function(report, chart_data_callback, options = {}) {
        if (!report.data || !report.data.length) return;

        const chart_type = this.get_selected_chart_type(report);
        const chart_data = chart_data_callback(report.data, report.filters, chart_type);
        
        if (!chart_data) return;

        this.render_chart(report, chart_data, chart_type, options);
    },

    /**
     * Get currently selected chart type
     */
    get_selected_chart_type: function(report) {
        if (report.chart_utils && report.chart_utils.chart_type_field) {
            return report.chart_utils.chart_type_field.get_value() || 'bar';
        }
        return 'bar';
    },

    /**
     * Render chart in report
     */
    render_chart: function(report, chart_data, chart_type, options = {}) {
        // Remove existing chart
        if (report.chart_wrapper) {
            report.chart_wrapper.remove();
        }

        // Create chart wrapper
        const chart_wrapper = $(`
            <div class="chart-wrapper" style="margin: 15px 0; padding: 15px; border: 1px solid #d1d8dd; border-radius: 3px;">
                <div class="chart-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h5 style="margin: 0;">${chart_data.title || __('Chart')}</h5>
                    <div class="chart-controls">
                        <button class="btn btn-xs btn-default chart-fullscreen" title="${__('Fullscreen')}">
                            <i class="fa fa-expand"></i>
                        </button>
                        <button class="btn btn-xs btn-default chart-download" title="${__('Download')}">
                            <i class="fa fa-download"></i>
                        </button>
                    </div>
                </div>
                <div class="chart-container"></div>
            </div>
        `);

        // Insert chart after filters
        if (report.page.wrapper.find('.report-wrapper').length) {
            chart_wrapper.insertBefore(report.page.wrapper.find('.report-wrapper'));
        } else {
            chart_wrapper.prependTo(report.page.wrapper.find('.page-content'));
        }

        // Create chart configuration
        const chart_config = this.create_chart_config(chart_data.data, {
            title: chart_data.title,
            type: chart_type,
            height: options.height || 300,
            colors: options.colors || this.color_schemes.stewardpro,
            ...chart_data.options
        });

        // Render chart
        const chart = new frappe.Chart(chart_wrapper.find('.chart-container')[0], chart_config);

        // Store references
        report.chart_wrapper = chart_wrapper;
        report.chart = chart;

        // Add event handlers
        chart_wrapper.find('.chart-fullscreen').click(() => {
            this.show_fullscreen_chart(chart_config);
        });

        chart_wrapper.find('.chart-download').click(() => {
            this.download_chart(chart, chart_data.title || 'chart');
        });

        // Auto-hide chart if no data
        if (!chart_data.data.labels || chart_data.data.labels.length === 0) {
            chart_wrapper.hide();
        }
    },

    /**
     * Toggle chart visibility
     */
    toggle_chart_visibility: function(report) {
        if (report.chart_wrapper) {
            report.chart_wrapper.toggle();
        }
    },

    /**
     * Show chart in fullscreen modal
     */
    show_fullscreen_chart: function(chart_config) {
        const dialog = new frappe.ui.Dialog({
            title: __('Chart - {0}', [chart_config.title || __('Report Chart')]),
            size: 'extra-large',
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'chart_html'
                }
            ]
        });

        dialog.show();

        // Create fullscreen chart
        const fullscreen_config = Object.assign({}, chart_config, {
            height: 500
        });

        setTimeout(() => {
            const chart_container = dialog.fields_dict.chart_html.$wrapper[0];
            new frappe.Chart(chart_container, fullscreen_config);
        }, 100);
    },

    /**
     * Download chart as image
     */
    download_chart: function(chart, filename) {
        if (chart && chart.export) {
            chart.export();
        } else {
            frappe.msgprint(__('Chart export not available'));
        }
    },

    /**
     * Export chart functionality
     */
    export_chart: function(report) {
        if (report.chart) {
            this.download_chart(report.chart, 'stewardpro_chart');
        } else {
            frappe.msgprint(__('No chart available to export'));
        }
    },

    /**
     * Process data for different chart types
     */
    process_chart_data: function(data, chart_type, options = {}) {
        if (!data || !data.length) return null;

        switch (chart_type) {
            case 'pie':
            case 'donut':
                return this.process_pie_data(data, options);
            case 'line':
            case 'area':
                return this.process_line_data(data, options);
            case 'bar':
            default:
                return this.process_bar_data(data, options);
        }
    },

    /**
     * Process data for pie/donut charts
     */
    process_pie_data: function(data, options = {}) {
        const labels = [];
        const values = [];

        data.forEach(row => {
            if (row[options.label_field] && row[options.value_field]) {
                labels.push(row[options.label_field]);
                values.push(row[options.value_field]);
            }
        });

        return {
            labels: labels,
            datasets: [{
                values: values
            }]
        };
    },

    /**
     * Process data for line/area charts
     */
    process_line_data: function(data, options = {}) {
        const labels = [];
        const datasets = {};

        data.forEach(row => {
            const label = row[options.label_field];
            if (label && !labels.includes(label)) {
                labels.push(label);
            }

            options.value_fields.forEach(field => {
                if (!datasets[field.name]) {
                    datasets[field.name] = {
                        name: field.label || field.name,
                        values: []
                    };
                }
            });
        });

        // Fill dataset values
        labels.forEach(label => {
            const row = data.find(r => r[options.label_field] === label);
            options.value_fields.forEach(field => {
                datasets[field.name].values.push(row ? (row[field.name] || 0) : 0);
            });
        });

        return {
            labels: labels,
            datasets: Object.values(datasets)
        };
    },

    /**
     * Process data for bar charts
     */
    process_bar_data: function(data, options = {}) {
        return this.process_line_data(data, options); // Same structure as line charts
    },

    /**
     * Format currency for tooltips
     */
    format_currency: function(value) {
        return frappe.format(value, { fieldtype: 'Currency' });
    },

    /**
     * Format percentage for tooltips
     */
    format_percentage: function(value) {
        return frappe.format(value, { fieldtype: 'Percent' });
    }
};

// Auto-initialize chart utilities when document is ready
$(document).ready(function() {
    // Add global CSS for charts
    if (!$('#stewardpro-chart-styles').length) {
        $('<style id="stewardpro-chart-styles">')
            .text(`
                .chart-wrapper {
                    background: #fff;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .chart-header h5 {
                    color: #2E7D32;
                    font-weight: 600;
                }
                .chart-controls .btn {
                    margin-left: 5px;
                }
                .chart-fullscreen-modal .modal-dialog {
                    max-width: 90vw;
                }
            `)
            .appendTo('head');
    }
});
