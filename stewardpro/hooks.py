app_name = "stewardpro"
app_title = "StewardPro"
app_publisher = "Innocent P Metumba"
app_description = "StewardPro"
app_email = "innocentphenelist@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "stewardpro",
		"logo": "/assets/stewardpro/assets/img/stewardpro.svg",
		"title": "StewardPro",
		"route": "/app/stewardpro",
		# "has_permission": "stewardpro.api.permission.has_app_permission"
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/stewardpro/css/stewardpro.css"
app_include_js = "/assets/stewardpro/js/chart_utils.js"

# include js, css files in header of web template
# web_include_css = "/assets/stewardpro/css/stewardpro.css"
# web_include_js = "/assets/stewardpro/js/stewardpro.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "stewardpro/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
	"Member" : "stewardpro/stewardpro/doctype/member/member_list.js",
	"Tithes and Offerings" : "stewardpro/stewardpro/doctype/tithes_and_offerings/tithes_and_offerings_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "stewardpro/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "home"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }


# Workspace Configuration
# -----------------------
# Set the default workspace for the module
module_default_workspace = "stewardpro"	

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "stewardpro.utils.jinja_methods",
# 	"filters": "stewardpro.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = ""
after_install = [
    "stewardpro.patches.import_departments.execute",
    "stewardpro.patches.create_roles.execute",
    "stewardpro.patches.create_demo_members.execute"
]

after_migrate = [
    "stewardpro.patches.import_departments.execute",
    "stewardpro.patches.create_roles.execute",
    "stewardpro.patches.create_demo_members.execute"
]

# Uninstallation
# ------------

# before_uninstall = "stewardpro.uninstall.before_uninstall"
# after_uninstall = "stewardpro.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "stewardpro.utils.before_app_install"
# after_app_install = "stewardpro.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "stewardpro.utils.before_app_uninstall"
# after_app_uninstall = "stewardpro.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "stewardpro.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# Treasury Budget sync hooks for Department Budget
doc_events = {
	"Department Budget": {
		"after_insert": "stewardpro.stewardpro.doctype.treasury_budget.sync.handle_department_budget_change",
		"on_update": "stewardpro.stewardpro.doctype.treasury_budget.sync.handle_department_budget_change",
		"on_trash": "stewardpro.stewardpro.doctype.treasury_budget.sync.handle_department_budget_delete"
	}
}
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"stewardpro.stewardpro.doctype.fiscal_year.fiscal_year.auto_create_fiscal_year"
	],
	"cron": {
		"0 0 * * 6": "stewardpro.stewardpro.tasks.send_weekly_sms_notification"
	}
}

# Testing
# -------

# before_tests = "stewardpro.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "stewardpro.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "stewardpro.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["stewardpro.utils.before_request"]
# after_request = ["stewardpro.utils.after_request"]

# Job Events
# ----------
# before_job = ["stewardpro.utils.before_job"]
# after_job = ["stewardpro.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"stewardpro.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

