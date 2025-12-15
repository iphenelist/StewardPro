// Copyright (c) 2025, StewardPro Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department Income', {
	refresh(frm) {
		// Add custom buttons or actions here
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('View Department'), function() {
				frappe.set_route('Form', 'Department', frm.doc.department);
			});
		}
	},

	department(frm) {
		// Fetch department code when department is selected
		if (frm.doc.department) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Department',
					filters: { name: frm.doc.department },
					fieldname: ['department_code']
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('department_code', r.message.department_code);
					}
				}
			});
		}
	},

	amount(frm) {
		// Validate amount is positive
		if (frm.doc.amount && frm.doc.amount <= 0) {
			frappe.msgprint(__('Amount must be greater than zero'));
			frm.set_value('amount', 0);
		}
	}
});

