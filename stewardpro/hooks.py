from . import __version__ as app_version

app_name = "stewardpro"
app_title = "StewardPro"
app_publisher = "StewardPro"
app_description = "SDA Church Management System - Membership, Sabbath School & Finance"
app_email = "info@stewardpro.com"
app_license = "mit"
app_logo_url = "/assets/stewardpro/pwa/icons/stewardpro-icon.svg"

add_to_apps_screen = [
	{
		"name": "stewardpro",
		"logo": app_logo_url,
		"title": app_title,
		"route": "/app/church-administration",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/stewardpro/pwa/stewardpro-pwa.css"
app_include_js = "/assets/stewardpro/pwa/stewardpro-pwa.js"

# include js, css files in header of web template
web_include_css = "/assets/stewardpro/pwa/stewardpro-pwa.css"
web_include_js = "/assets/stewardpro/pwa/stewardpro-pwa.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "stewardpro/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {
# 	"DocType": "public/js/doctype.js"
# }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
doctype_tree_js = {"Church Account": "public/js/church_account_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

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

after_install = "stewardpro.setup.after_install"
# before_uninstall = "stewardpro.uninstall.before_uninstall"
after_migrate = "stewardpro.setup.after_install"

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
# 	"Tithe and Offering Entry": {
# 		"on_submit": "stewardpro.api.sms.send_tithe_offering_receipt"
# 	},
# 	"Church Member": {
# 		"after_insert": "stewardpro.api.sms.send_member_welcome"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"stewardpro.api.sms.send_birthday_greetings",
		# Runs every day but internally checks for Saturday before creating remittance
		"stewardpro.api.remittance.create_weekly_remittance",
	],
}

# Testing
# -------

# before_tests = "stewardpro.install.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "stewardpro.event.get_events"
# }

# exempt linked doctypes from being automatically cancelled
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"stewardpro.auth.validate"
# ]
