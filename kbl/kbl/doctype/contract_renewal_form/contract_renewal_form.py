# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ContractRenewalForm(Document):
    def on_submit(self):
        approvers = []
        emp_user_id = frappe.db.get_value('Employee',{'name':self.employee_id},'user_id')
        hod_user_id = frappe.db.get_value('Employee',{'name':self.reports_to},'user_id')
        line_manager_1 = frappe.db.get_value('Employee',{'name':self.line_manager_1},'user_id')
        line_manager_2 = frappe.db.get_value('Employee',{'name':self.line_manager_2},'user_id')
        if line_manager_1:
            approvers.append(line_manager_1)
        
        if line_manager_2:
            approvers.append(line_manager_2)
        
        if self.head_hr:
            approvers.append(self.head_hr)

        if hod_user_id:
            approvers.append(hod_user_id)
    
        frappe.sendmail(
            # recipients='jothi.m@groupteampro.com',
            recipients = emp_user_id,
            cc=approvers, 
            subject="Contract Renewal Letter",
            message="""<p>Dear {}</p><br>
                <p>We are pleased to let you know that your contract has been renewed. Please find the attached contract renewal letter for information and records. Kindly send us the signed renewal letter as a token of your acceptance and share it with us at hrops@kblservices.in.</p><br>
                <p>In case of any assistance, please feel free to contact the HR department.</p><br><br>
                Regards,<br> HR Department,<br> KBL Services Ltd, Bengaluru-08041251494
            """.format(self.employee_name),
            attachments=[frappe.attach_print("Contract Renewal Form", self.name,file_name="Contract Renewal Form ", print_format="Contract Renewal Form")]
           
        )
    

    pass
