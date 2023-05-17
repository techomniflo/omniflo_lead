from . import __version__ as app_version

app_name = "omniflo_lead"
app_title = "Omniflo Lead"
app_publisher = "Omniflo"
app_description = "Omniflo Lead"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "vivekchole@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omniflo_lead/css/omniflo_lead.css"
app_include_js = ["/assets/omniflo_lead/customer.js","/assets/omniflo_lead/sales_invoice.js","/assets/omniflo_lead/sales_order.js"]

# include js, css files in header of web template
# web_include_css = "/assets/omniflo_lead/css/omniflo_lead.css"
# web_include_js = "/assets/omniflo_lead/js/omniflo_lead.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omniflo_lead/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js={"Customer": "public/js/customer.js","Sales Invoice":"public/js/sales_invoice.js","Sales Order":"public/js/sales_order.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omniflo_lead.utils.jinja_methods",
# 	"filters": "omniflo_lead.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "omniflo_lead.install.before_install"
# after_install = "omniflo_lead.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omniflo_lead.notifications.get_notification_config"

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

override_doctype_class = {
	"Stock Ledger Entry": "omniflo_lead.omniflo_lead.doctype_class_override.stock_ledger_entry.CustomStockLedgerEntry",
	"Purchase Receipt": "omniflo_lead.omniflo_lead.doctype_class_override.purchase_receipt.CustomPurchaseReceipt",
	"Stock Entry": "omniflo_lead.omniflo_lead.doctype_class_override.stock_entry.CustomStockEntry",
    "Sales Order":"omniflo_lead.omniflo_lead.doctype_class_override.sales_order.CustomSalesOrder"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
    "Sales Invoice":{
        "on_submit": "omniflo_lead.omniflo_lead.doctype_events.sales_invoice.on_submit",
		"on_cancel": "omniflo_lead.omniflo_lead.doctype_events.sales_invoice.on_cancel",
		"before_submit": "omniflo_lead.omniflo_lead.doctype_events.sales_invoice.before_submit"
    },
	"File":{
		"after_insert": "omniflo_lead.omniflo_lead.doctype_events.file.file_upload_to_s3"
	},
	"Purchase Receipt":{
	"on_submit":"omniflo_lead.omniflo_lead.doctype_events.purchase_receipt.on_submit"
	}

}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"omniflo_lead.tasks.all"
# 	],
	"cron": {"0 */12 * * *":["omniflo_lead.omniflo_lead.doctype.day_wise_sales.day_wise_sales.day_sales"]
	}
# 	"hourly": [
# 		"omniflo_lead.tasks.hourly"
# 	],
# 	"weekly": [
# 		"omniflo_lead.tasks.weekly"
# 	],
# 	"monthly": [
# 		"omniflo_lead.tasks.monthly"
# 	],
}

# Testing
# -------

# before_tests = "omniflo_lead.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omniflo_lead.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omniflo_lead.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


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
# 	"omniflo_lead.auth.validate"
# ]

