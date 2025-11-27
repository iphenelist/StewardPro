// Copyright (c) 2025, Innocent P Metumba and contributors
// For license information, please see license.txt

frappe.ui.form.on("Department Expense", {
	refresh: function(frm) {
		// Set item filter for expense details table
		set_item_filter_for_expense_details(frm);

		// Set budget reference filter based on department
		set_budget_reference_filter(frm);
		frm.set_value("approval_date", frappe.datetime.get_today());
		frm.set_query('approved_by', () => {
			return {
				filters: {
					"role": ["in",["Member", "Elder", "Treasurer"]]
				}
			}
		})
	},

	department: function(frm) {
		// Clear budget reference when department changes
		frm.set_value('budget_reference', '');

		// Clear existing expense details when department changes
		frm.clear_table('expense_details');
		frm.refresh_field('expense_details');

		// Update filters
		set_item_filter_for_expense_details(frm);
		set_budget_reference_filter(frm);
	},

	budget_reference: function(frm) {
		// Show budget items popup when budget reference is selected
		if (frm.doc.budget_reference) {
			show_budget_items_popup(frm);
		}
	}
});

frappe.ui.form.on("Department Expense Detail", {
	item: function(frm, cdt, cdn) {
		// Auto-populate description and unit price from item
		let row = locals[cdt][cdn];
		if (row.item) {
			frappe.db.get_value('Item', row.item, ['description', 'standard_cost'], function(r) {
				if (r) {
					if (r.description && !row.expense_description) {
						frappe.model.set_value(cdt, cdn, 'expense_description', r.description);
					}
					if (r.standard_cost && !row.unit_price) {
						frappe.model.set_value(cdt, cdn, 'unit_price', r.standard_cost);
					}
				}
			});
		}
	},

	quantity: function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn);
	},

	unit_price: function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn);
	},

	expense_details_remove: function(frm) {
		calculate_total_amount(frm);
	}
});

function set_item_filter_for_expense_details(frm) {
	if (frm.doc.department) {
		frm.set_query('item', 'expense_details', function() {
			return {
				filters: {
					'department': frm.doc.department,
					'is_active': 1
				}
			};
		});
	}
}

function calculate_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.quantity && row.unit_price) {
		let amount = row.quantity * row.unit_price;
		frappe.model.set_value(cdt, cdn, 'amount', amount);

		// Trigger total calculation in parent
		calculate_total_amount(frm);
	}
}

function calculate_total_amount(frm) {
	let total = 0;
	frm.doc.expense_details.forEach(function(row) {
		if (row.amount) {
			total += row.amount;
		}
	});
	frm.set_value('total_amount', total);
}

function set_budget_reference_filter(frm) {
	if (frm.doc.department) {
		frm.set_query('budget_reference', function() {
			return {
				filters: {
					'department': frm.doc.department,
					'is_active': 1
				}
			};
		});
	}
}

function show_budget_items_popup(frm) {
	// Get budget items from the selected budget
	frappe.call({
		method: 'stewardpro.stewardpro.doctype.department_expense.department_expense.get_budget_items_for_reference',
		args: {
			budget_reference: frm.doc.budget_reference
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				show_budget_items_dialog(frm, r.message);
			} else {
				frappe.msgprint(__('No budget items found for the selected budget.'));
			}
		}
	});
}

function show_budget_items_dialog(frm, budget_items) {
	let dialog = new frappe.ui.Dialog({
		title: __('Select Budget Items'),
		size: 'large',
		fields: [
			{
				fieldname: 'budget_items_html',
				fieldtype: 'HTML',
				options: get_budget_items_html(budget_items)
			}
		],
		primary_action_label: __('Add Selected Items'),
		primary_action: function() {
			let selected_items = [];
			dialog.$wrapper.find('input[type="checkbox"]:checked').each(function() {
				let item_data = JSON.parse($(this).attr('data-item'));
				let quantity = parseFloat($(this).closest('tr').find('.quantity-input').val()) || 1;
				item_data.quantity = quantity;
				selected_items.push(item_data);
			});

			if (selected_items.length > 0) {
				add_items_to_expense_details(frm, selected_items);
				dialog.hide();
			} else {
				frappe.msgprint(__('Please select at least one item.'));
			}
		}
	});

	dialog.show();

	// Add event handlers for checkboxes and quantity inputs
	dialog.$wrapper.find('input[type="checkbox"]').on('change', function() {
		let $row = $(this).closest('tr');
		if ($(this).is(':checked')) {
			$row.addClass('selected-row');
			$row.find('.quantity-input').prop('disabled', false);
		} else {
			$row.removeClass('selected-row');
			$row.find('.quantity-input').prop('disabled', true);
		}
		update_selected_total(dialog);
	});

	// Add event handler for quantity changes to update amount preview
	dialog.$wrapper.find('.quantity-input').on('input', function() {
		let $input = $(this);
		let quantity = parseFloat($input.val()) || 0;
		let unitPrice = parseFloat($input.attr('data-unit-price')) || 0;
		let amount = quantity * unitPrice;

		$input.closest('tr').find('.amount-preview').text(format_currency(amount));
		update_selected_total(dialog);
	});

	// Function to update selected total
	function update_selected_total(dialog) {
		let total = 0;
		dialog.$wrapper.find('input[type="checkbox"]:checked').each(function() {
			let $row = $(this).closest('tr');
			let quantity = parseFloat($row.find('.quantity-input').val()) || 0;
			let unitPrice = parseFloat($row.find('.quantity-input').attr('data-unit-price')) || 0;
			total += quantity * unitPrice;
		});
		dialog.$wrapper.find('#selected-total').text(format_currency(total));
	}
}

function get_budget_items_html(budget_items) {
	let html = `
		<div class="budget-items-container">
			<table class="table table-bordered">
				<thead>
					<tr>
						<th width="3%">
							<input type="checkbox" id="select-all-items" />
						</th>
						<th width="16%">${__('Item')}</th>
						<th width="18%">${__('Description')}</th>
						<th width="7%">${__('Budget Qty')}</th>
						<th width="9%">${__('Unit Price')}</th>
						<th width="9%">${__('Budgeted')}</th>
						<th width="8%">${__('Remaining')}</th>
						<th width="10%">${__('Expense Qty')}</th>
						<th width="10%">${__('Amount')}</th>
					</tr>
				</thead>
				<tbody>
	`;

	budget_items.forEach(function(item) {
		html += `
			<tr>
				<td>
					<input type="checkbox"
						   data-item='${JSON.stringify(item)}'
						   class="item-checkbox" />
				</td>
				<td>${item.item_name || item.item}</td>
				<td>${item.description || ''}</td>
				<td class="text-center">${item.quantity || 1}</td>
				<td>${format_currency(item.unit_price)}</td>
				<td>${format_currency(item.budgeted_amount)}</td>
				<td>${format_currency(item.remaining_amount)}</td>
				<td>
					<input type="number"
						   class="form-control quantity-input"
						   value="${item.quantity || 1}"
						   min="1"
						   step="1"
						   data-unit-price="${item.unit_price}"
						   disabled />
				</td>
				<td class="amount-preview text-right">
					${format_currency((item.quantity || 1) * item.unit_price)}
				</td>
			</tr>
		`;
	});

	html += `
				</tbody>
				<tfoot>
					<tr class="table-info">
						<td colspan="9" class="text-right"><strong>${__('Selected Total:')}</strong></td>
						<td class="text-right"><strong><span id="selected-total">0.00</span></strong></td>
					</tr>
				</tfoot>
			</table>
		</div>
		<style>
			.budget-items-container {
				max-height: 400px;
				overflow-y: auto;
			}
			.selected-row {
				background-color: #f8f9fa;
			}
			.quantity-input {
				width: 80px;
			}
		</style>
		<script>
			// Select all functionality
			$(document).on('change', '#select-all-items', function() {
				let isChecked = $(this).is(':checked');
				$('.item-checkbox').prop('checked', isChecked).trigger('change');
			});
		</script>
	`;

	return html;
}

function add_items_to_expense_details(frm, selected_items) {
	selected_items.forEach(function(item) {
		let row = frm.add_child('expense_details');
		row.item = item.item;
		row.expense_description = item.item_name || item.item;
		row.quantity = item.quantity;
		row.unit_price = item.unit_price;
		row.amount = item.quantity * item.unit_price;
	});

	frm.refresh_field('expense_details');
	calculate_total_amount(frm);

	frappe.show_alert({
		message: __('Added {0} items to expense details', [selected_items.length]),
		indicator: 'green'
	});
}
