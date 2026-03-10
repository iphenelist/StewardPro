// Copyright (c) 2026, StewardPro and contributors
// Church Account — custom tree view settings with live balance display

frappe.treeview_settings["Church Account"] = {
	breadcrumb: "Church Finance",
	title: __("Chart of Accounts"),

	// Use our custom API so that computed balances are included in every node
	get_tree_nodes:
		"stewardpro.church_finance.doctype.church_account.church_account.get_children",

	// extend_toolbar:true adds our button alongside Edit/Add Child/Rename/Delete
	extend_toolbar: true,
	toolbar: [
		{
			label: __("Refresh Balances"),
			condition: function (node) {
				return (
					frappe.user.has_role("Treasurer") ||
					frappe.user.has_role("System Manager")
				);
			},
			click: function (node) {
				frappe.call({
					method: "stewardpro.church_finance.doctype.church_account.church_account.refresh_all_balances",
					freeze: true,
					freeze_message: __("Refreshing account balances…"),
					callback: function () {
						cur_tree.load_children(cur_tree.root_node, true);
					},
				});
			},
		},
	],

	// Colour coding per account type (used in onrender)
	_type_style: {
		Income: { bg: "#e8f5e9", fg: "#2e7d32" },
		Expense: { bg: "#fff3e0", fg: "#e65100" },
		Asset: { bg: "#e3f2fd", fg: "#1565c0" },
		Liability: { bg: "#fce4ec", fg: "#b71c1c" },
	},

	// Called each time a tree node is rendered
	onrender: function (node) {
		var data = node.data || {};
		if (!data.value) return; // skip virtual root

		// Remove a previously injected badge to avoid duplicates on refresh
		node.$li.find(".sp-account-meta").remove();

		var balance = flt(data.balance || 0);
		var atype = data.account_type || "";
		var style = frappe.treeview_settings["Church Account"]._type_style[atype] || {
			bg: "#f5f5f5",
			fg: "#555",
		};

		// Balance colour: green if positive, red if negative,
		// orange for expense (spending shown as positive)
		var bal_color = "#4CAF50";
		if (atype === "Expense") {
			bal_color = "#FF9800";
		} else if (balance < 0) {
			bal_color = "#F44336";
		}

		var currency = (frappe.boot.sysdefaults || {}).currency || "";
		var formatted_bal = format_currency(balance, currency);

		var html =
			'<span class="sp-account-meta" style="float:right; margin-left:10px; white-space:nowrap;">' +
			// Account-type chip
			(atype
				? '<span style="font-size:10px; background:' +
				  style.bg +
				  "; color:" +
				  style.fg +
				  '; border-radius:3px; padding:1px 6px; margin-right:8px;">' +
				  __(atype) +
				  "</span>"
				: "") +
			// Balance value
			'<span style="font-size:12px; font-weight:600; color:' +
			bal_color +
			';">' +
			formatted_bal +
			"</span>" +
			"</span>";

		// Append inside the tree-link span so it stays on the same row
		node.$li.find(".tree-link").append(html);
	},
};
