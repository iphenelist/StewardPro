from frappe import _


def get_data():
	return [
		{
			"module_name": "Church Administration",
			"type": "module",
			"label": _("Church Administration"),
		},
		{
			"module_name": "Sabbath School",
			"type": "module",
			"label": _("Sabbath School"),
		},
		{
			"module_name": "Church Finance",
			"type": "module",
			"label": _("Church Finance"),
		},
	]
