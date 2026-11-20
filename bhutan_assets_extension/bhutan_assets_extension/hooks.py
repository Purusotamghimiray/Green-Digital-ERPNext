app_name = "bhutan_assets_extension"
app_title = "Bhutan Assets Extension"
app_publisher = "Purusotam Ghimiray"
app_description = "bhutan_assets_extension"
app_email = "purusotamghimiray@druksmart.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "bhutan_assets_extension",
# 		"logo": "/assets/bhutan_assets_extension/logo.png",
# 		"title": "Bhutan Assets Extension",
# 		"route": "/bhutan_assets_extension",
# 		"has_permission": "bhutan_assets_extension.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bhutan_assets_extension/css/bhutan_assets_extension.css"
# app_include_js = "/assets/bhutan_assets_extension/js/bhutan_assets_extension.js"

# include js, css files in header of web template
# web_include_css = "/assets/bhutan_assets_extension/css/bhutan_assets_extension.css"
# web_include_js = "/assets/bhutan_assets_extension/js/bhutan_assets_extension.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "bhutan_assets_extension/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {"Asset": "public/js/asset_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "bhutan_assets_extension/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "bhutan_assets_extension.utils.jinja_methods",
# 	"filters": "bhutan_assets_extension.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "bhutan_assets_extension.install.before_install"
# after_install = "bhutan_assets_extension.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "bhutan_assets_extension.uninstall.before_uninstall"
# after_uninstall = "bhutan_assets_extension.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "bhutan_assets_extension.utils.before_app_install"
# after_app_install = "bhutan_assets_extension.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "bhutan_assets_extension.utils.before_app_uninstall"
# after_app_uninstall = "bhutan_assets_extension.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bhutan_assets_extension.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bhutan_assets_extension.tasks.all"
# 	],
# 	"daily": [
# 		"bhutan_assets_extension.tasks.daily"
# 	],
# 	"hourly": [
# 		"bhutan_assets_extension.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bhutan_assets_extension.tasks.weekly"
# 	],
# 	"monthly": [
# 		"bhutan_assets_extension.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "bhutan_assets_extension.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "bhutan_assets_extension.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bhutan_assets_extension.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "bhutan_assets_extension.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["bhutan_assets_extension.utils.before_request"]
# after_request = ["bhutan_assets_extension.utils.after_request"]

# Job Events
# ----------
# before_job = ["bhutan_assets_extension.utils.before_job"]
# after_job = ["bhutan_assets_extension.utils.after_job"]

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
# 	"bhutan_assets_extension.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

