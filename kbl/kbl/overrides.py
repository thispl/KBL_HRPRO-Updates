from email import message
import frappe
from frappe import _
import datetime, math
from erpnext.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from frappe.utils import cstr, add_days, date_diff,format_datetime,ceil,flt
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime, format_date,get_time)
from erpnext.hr.doctype.job_applicant.job_applicant import JobApplicant

# class PayrollEntry(PayrollEntry):
# 	pass
	# def on_submit(self):
	# 	frappe.errprint('frappe.errprint("INACTIVE")')
	# 	employees = [emp.employee for emp in self.employees]
	# 	inactive_employees = []
	# 	for emp in employees:
	# 		employee_doc = frappe.get_doc("Employee", emp)
	# 		if employee_doc.status == "Inactive":
	# 			inactive_employees.append(emp)
	# 	if inactive_employees:
	# 		frappe.errprint("INACTIVE")
	# 		inactive_emp_numbers = ", ".join(inactive_employees)
	# 		frappe.throw(_("Employee(s) with inactive state found: <b>{0}</b> .Mark them left and try to run Payroll Entry").format(inactive_emp_numbers))


class JobApplicant(JobApplicant):
	def autoname(self):
		# keys = filter(None, (self.applicant_name, self.email_id, self.job_title))
		# if not keys:
		#     frappe.throw(_("Name or Email is mandatory"), frappe.NameError)
		# self.name = " - ".join(keys)
		print("Welcome")

	def check_email_id_is_unique(self):
		# if self.email_id:
		#     names = frappe.db.sql_list("""select name from `tabJob Applicant`
		#         where email_id=%s and name!=%s and job_title=%s""", (self.email_id, self.name, self.job_title))

		#     if names:
		#         frappe.throw(_("Email Address must be unique, already exists for {0}").format(comma_and(names)), frappe.DuplicateEntryError)
		print("Welcome")