# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff, add_months,today ,nowtime,nowdate, format_date, add_days
from frappe.model.document import Document

class PerformanceImprovementPlan(Document):
	pass
	def after_insert(self):
		doc_count=frappe.db.sql("select count(*) as count from `tabPerformance Improvement Plan` where employee = '%s'"%(self.employee),as_dict=True)
		if doc_count[0].count > 2:
			if self.minimum_score > self.achieved_points:
				frappe.errprint(doc_count[0])
				if self.branch_manager_mail_id:
					pip_mail(self.name,self.employee,self.branch_manager_mail_id,self.employee_name,self.cc1,self.cc2,self.cc3)
				else:
					pip_mail(self.name,self.employee,None,self.employee_name,self.cc1,self.cc2,self.cc3)

@frappe.whitelist()
def pip_mail(name,employee,branch_manager_mail_id,emp_name,cc1,cc2,cc3):
    date = today()
    print(date)
    cc=''
    cc_1=''
    cc_2=''
    cc_3=''
    if cc1 is not None:
        cc_1=cc1
    if cc2 is not None:
        cc_2=cc2
    if cc3 is not None:
        cc_3=cc3
    if branch_manager_mail_id is not None:
        cc=branch_manager_mail_id
    user_id = frappe.get_value('Employee',{ "name":employee},['user_id'])
    frappe.sendmail(
        recipients=[user_id],
        # recipients=[cc],
        # recipients=['giftyannie6@gmail.com'],
        cc = [cc,cc_1,cc_2,cc_3],
        subject="PIP Letter",
        message="""<p>Dear {},</p>
            <p>Kindly find the attached document of PIP Letter for your reference
            </p><br> Regards <br>KBL Service Limited""".format(emp_name),
        now=True,
        attachments=[frappe.attach_print("Performance Improvement Plan", name,
            file_name=name, print_format="PIP Letter")]
    )
