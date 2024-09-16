# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WarningLetter(Document):
	def after_insert(self):
		document = frappe.db.exists("Warning Letter",{"employee",self.employee})
		if not document:
			count = frappe.db.sql(""" SELECT COUNT(warning) AS count FROM `tabWarning Letter` WHERE employee=%s ORDER BY creation DESC """, (self.employee,), as_dict=True)
			if count:
				warning_count = count[0]['count'] + 1
				frappe.db.set_value("Warning Letter", self.name, "warning", warning_count)

@frappe.whitelist()
def warning_letter_mail(name,user_id, dep_id=None,branch_mail_id = None):
	frappe.errprint(dep_id)
	frappe.sendmail(
		recipients=user_id,
		cc=[dep_id,branch_mail_id],
		subject="Warning Letter",
		message="""<p>Dear Sir/Madam,</p>
			<p>Kindly find the attached document of Warning Letter for your reference
			</p><br> Regards, <br> HR Department<br>KBL Services Ltd, Bengaluru""",
		now=True,
		attachments=[frappe.attach_print("Warning Letter", name,
			file_name=name, print_format="Warning Letter")]
	)
	return "Email Successfully Sent"

@frappe.whitelist()
def new_occurrence_count(type,emp):
    frappe.errprint("hi")
    if frappe.db.exists("Warning Letter", {"employee":emp,"issue_type":type}):
        count = frappe.db.sql("""SELECT count(*) as count FROM `tabWarning Letter` WHERE employee = %s AND issue_type=%s ORDER BY creation DESC LIMIT 1""",(emp,type), as_dict=True)
        frappe.errprint(count[0]['count'])
        count = count[0]['count'] + 1
    else:
        count = 1
    return count
