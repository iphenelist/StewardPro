// Copyright (c) 2024, StewardPro Team and contributors
// For license information, please see license.txt

frappe.listview_settings['Item'] = {
	add_fields: ["is_active", "category", "department", "standard_cost"],
	filters: [["is_active", "=", 1]],
	
	get_indicator: function(doc) {
		if (doc.is_active) {
			return [__("Active"), "green", "is_active,=,1"];
		} else {
			return [__("Inactive"), "red", "is_active,=,0"];
		}
	},
	
	formatters: {
		standard_cost: function(value) {
			if (value) {
				return format_currency(value);
			}
			return "";
		}
	},
	
	onload: function(listview) {
		// Add custom buttons to list view
		listview.page.add_menu_item(__("Items by Department"), function() {
			show_items_by_department();
		});
		
		listview.page.add_menu_item(__("Items by Category"), function() {
			show_items_by_category();
		});
	}
};

function show_items_by_department() {
	frappe.call({
		method: "stewardpro.church_management.doctype.item.item.get_active_items",
		callback: function(r) {
			if (r.message) {
				let items_by_dept = {};
				r.message.forEach(function(item) {
					if (!items_by_dept[item.department]) {
						items_by_dept[item.department] = [];
					}
					items_by_dept[item.department].push(item);
				});
				
				let html = '<div class="row">';
				Object.keys(items_by_dept).forEach(function(dept) {
					html += '<div class="col-md-6">';
					html += '<h5>' + dept + '</h5>';
					html += '<ul>';
					items_by_dept[dept].forEach(function(item) {
						html += '<li>' + item.item_name + ' (' + item.category + ')';
						if (item.standard_cost) {
							html += ' - ' + format_currency(item.standard_cost);
						}
						html += '</li>';
					});
					html += '</ul></div>';
				});
				html += '</div>';
				
				frappe.msgprint({
					title: __("Items by Department"),
					message: html,
					wide: true
				});
			}
		}
	});
}

function show_items_by_category() {
	frappe.call({
		method: "stewardpro.church_management.doctype.item.item.get_active_items",
		callback: function(r) {
			if (r.message) {
				let items_by_cat = {};
				r.message.forEach(function(item) {
					if (!items_by_cat[item.category]) {
						items_by_cat[item.category] = [];
					}
					items_by_cat[item.category].push(item);
				});
				
				let html = '<div class="row">';
				Object.keys(items_by_cat).forEach(function(cat) {
					html += '<div class="col-md-6">';
					html += '<h5>' + cat + '</h5>';
					html += '<ul>';
					items_by_cat[cat].forEach(function(item) {
						html += '<li>' + item.item_name + ' (' + item.department + ')';
						if (item.standard_cost) {
							html += ' - ' + format_currency(item.standard_cost);
						}
						html += '</li>';
					});
					html += '</ul></div>';
				});
				html += '</div>';
				
				frappe.msgprint({
					title: __("Items by Category"),
					message: html,
					wide: true
				});
			}
		}
	});
}
