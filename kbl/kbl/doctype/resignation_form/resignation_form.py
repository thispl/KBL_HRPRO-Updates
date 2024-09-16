# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ResignationForm(Document):
	def after_insert(self):
		self.relieving_form_mail()
		self.relieving_form_hod()
	def on_submit(self):
		self.relieving_form_approval()
		self.relieving_letter_mail()
		self.update_status_left()
	def relieving_form_approval(self):
			hod=frappe.db.get_value("Employee",{"name":self.reports_to},['user_id'])
			frappe.errprint("working")
			frappe.sendmail(
						recipients=self.user_id,
						cc='',  
						subject='Approval of Resignation and Exit Checklist ',
						message="""
							<b>Dear {},</b><br><br>
							Find the attached resignation letter for your reference <br><br>
							We would like to inform you that your resignation has been accepted. <br><br>
							As part of the exit process, please ensure that the following items are completed: <br><br>
							<b>Office Note:</b> A formal office note has been prepared documenting your resignation. <br><br>
							<b>No Objection Certificate (NOC):</b> The NOC has been prepared, indicating no objection to your departure from the company.<br><br> 
							<b>Exit Interview Checklist:</b> The exit interview need to be completed to gather feedback and insights from your experience with us. <br><br> 
							We wish you the best of luck in your future endeavours. <br>

							
							Thanks & Regards,<br>
							HR Department,<br>
							KBL Services Ltd, Bengaluru<br>
							*This email has been automatically generated. Please do not reply*
						""".format(self.employee_name),
				attachments=[frappe.attach_print("Resignation Form", self.name,file_name="Resignation Letter", print_format="Resignation")]
					)
	def relieving_letter_mail(self):
		frappe.errprint("working")
		frappe.sendmail(
					recipients=self.user_id,
					cc=self.branch_mail,
					subject='Relieving Letter ',
					message="""
						<b>Dear {},</b><br><br>
						Your Resignation request got approved, Kindly find the attached relieving letter for your reference<br><br>
						Thanks & Regards,<br>
						HR Department<br>
						KBL Services Ltd, Bengaluru<br>
						*This email has been automatically generated. Please do not reply*
					""".format(self.employee_name),
			attachments=[frappe.attach_print("Resignation Form", self.name,file_name="Relieving Letter", print_format="Relieving Letter")]
				)
	
	def update_status_left(self):
		frappe.db.set_value("Employee",self.name,"status","Left")
	def relieving_form_mail(self):
		hod=frappe.db.get_value("Employee",{"name":self.reports_to},['user_id'])
		frappe.sendmail(
					recipients=self.user_id,
					cc='',  
					subject='Acceptance of Resignation',
					message="""
						<b>Dear {},</b><br><br>
						We hope this email finds you well.<br><br>
						We would like to inform you that your resignation from KBL Services Limited has been taken ahead, but it does not mean that your resignation has been accepted.<br><br>
						We regret to learn that you have chosen to resign and will not be continuing your employment with KBL Services Limited. This letter serves as an acknowledgment of your resignation, and we will proceed with the necessary steps from here. <br><br>
						<b>Kindly apply for the No due and get approval. Once no due is approved,NOC Document will be shared through mail.Sign the NOC document ,upload it in your resignation form and submit it for approval.Then only Resignation will taken for review.</b><br><br>
						If you have any outstanding tasks or pending handovers, please ensure they are completed before your last working day. <br><br>
						We wish you all the best in your future endeavours. <br><br>
						Best regards,  <br>
						HR Department, <br>
						KBL Services Ltd, Bengaluru<br><br>

						
						*This email has been automatically generated. Please do not reply*
					""".format(self.employee_name)
					
				)
		
	def relieving_form_hod(self):
		hod = frappe.db.get_value("Employee", {"name": self.reports_to}, 'user_id')
		if hod:
			message = """
				<b>Dear Sir/ Madam,</b><br><br>
				We hope this email finds you well.<br><br>
				This is a resignation alert from {employee_name} - {employee_id}. We would like to inform you that your reportee has resigned from KBL Services Limited. This is the next process where the manager has to provide his/her approval or rejection.<br><br>
				After receiving the resignation acceptance, we will be sharing it with the HR head for final approval and processing of the Full and Final Settlement (F&F), based on their notice period. If they have any outstanding tasks or pending handovers, please ensure they are completed before the last working day as generated by the HR department. <br><br>
				Best regards, <br>
				HR Department, <br>
				KBL Services Ltd, Bengaluru<br><br>
				
				*This email has been automatically generated. Please do not reply*
			""".format(hod_email=hod, employee_name=self.employee_name, employee_id=self.employee)
			frappe.sendmail(
				recipients=[hod],
				cc='',
				subject='Resignation Alert',
				message=message
			)
        


@frappe.whitelist()
def update_relieving_date(date,employee,posting_date):
    frappe.db.set_value("Employee",employee,"relieving_date",date)
    frappe.db.set_value("Employee",employee,"exit_type","Resigned")
    frappe.db.set_value("Employee",employee,"resignation_letter_date",posting_date)