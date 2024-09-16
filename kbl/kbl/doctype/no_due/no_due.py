# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class NoDue(Document):
	def on_submit(self):
		hod=frappe.db.get_value("Employee",{"name":self.reports_to},['user_id'])
		frappe.sendmail(
					recipients=self.user_id,
					cc=hod if hod else [],  
					subject='No Objection Certificate (NOC) for {} '.format(self.employee_name),
					message="""
						<b>Dear {},</b><br><br>
						We hope this email finds you well.<br><br>
						Please find attached the NOC document for your review and signature. Once signed, attach the document in resignation form and sumbit for approval . Also Kindly return the document to {} by {}.   <br><br>
						Regards, <br>
						HR Department,<br>
						KBL Services Ltd, Bengaluru<br>
					""".format(self.employee_name,self.reports_to,self.last_working_date),
					now=True,
					attachments=[frappe.attach_print("No Due", self.name,
					file_name='NOC', print_format="NOC form")]
			)
		