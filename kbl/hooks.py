from . import __version__ as app_version

app_name = "kbl"
app_title = "KBL"
app_publisher = "TEAMPRO"
app_description = "Customizations for KBL"
app_icon = "octicon octicon-gear"
app_color = "grey"
app_email = "abdulla.pi@groupteampro.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/kbl/css/kbl_theme.css"
app_include_js = "/assets/kbl/js/kbl.js"

# include js, css files in header of web template
# web_include_css = "/assets/kbl/css/kbl.css"
# web_include_js = "/assets/kbl/js/kbl.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "kbl/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
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

# Installation
# ------------

# before_install = "kbl.install.before_install"
# after_install = "kbl.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kbl.notifications.get_notification_config"

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
	# "Payroll Entry": "kbl.kbl.overrides.PayrollEntry",
	"Job Applicant": "kbl.kbl.overrides.JobApplicant",

}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Employee": {
		"after_insert": "kbl.custom.create_employee_onboarding",
		"on_update": "kbl.custom.update_user",
		# "validate": "kbl.custom.inactive_employee",
	},
	"Job Applicant":{
		"after_insert": "kbl.custom.applicant_creation",
	},
	"Visit Report":{
		"on_submit": "kbl.custom.visit_report",
	},
	# "Employee":{
	# 	"after_insert":["kbl.custom.create_sick_leave_allocation","kbl.custom.create_privilege_leave_allocation"]
	# },
	"Attendance":{
		"after_insert":["kbl.custom.crm_att"],
        "validate":["kbl.custom.validate_block_att"]
	},

    "Salary Structure Assignment":{
        "on_submit": "kbl.custom.sal_structure",
	},
    # "Resignation Form":{
	# 	"on_submit":['kbl.custom.relieving_form_approval','kbl.custom.relieving_letter_mail','kbl.custom.update_status_left'],
    #     "after_insert":["kbl.custom.relieving_form_mail","kbl.custom.relieving_form_hod"],
	# },
    # "No Due":{
    #     "on_submit": "kbl.custom.noc_form",
	# },
    "Job Offer":{
        'on_submit':['kbl.custom.job_offer_emails','kbl.custom.joboffer_mail'],
        "after_insert":'kbl.custom.attachments_applicant'
	},
    "Job Opening":{
        "after_insert": "kbl.custom.job_opening_rename",
	},
    "Leave Application":{
		"validate": ["kbl.custom.compoff_restriction","kbl.custom.leave_restriction_lwp_after","kbl.custom.leave_restriction_lwp_before"],
	},
    

}

# Scheduled Tasks
# ---------------

scheduler_events = {
	
	# "monthly": [
		
# 		"kbl.tasks.monthly"

	# ],
	
# 	"all": [
# 		"kbl.tasks.all"
# 	],
	"daily": [
		# "kbl.custom.update_previous_leave_allocation_manually",
		"kbl.custom.create_privilege_and_sick_leave_1",

		
		# "kbl.tasks.daily"
	],
# 	"hourly": [
# 		"kbl.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kbl.tasks.weekly"
# 	]
	"monthly": [
		# "kbl.tasks.monthly"
        "kbl.custom.create_privilege_leave"
    ]
}



# Testing
# -------

# before_tests = "kbl.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "kbl.event.get_events"
# }
jenv = {
	"methods": [
		"get_monthly_points:kbl.custom.get_monthly_points",
		"get_count:kbl.custom.get_count",
		"get_date:kbl.custom.get_date"
    ]
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "kbl.task.get_dashboard_data"
# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"kbl.auth.validate"
# ]

