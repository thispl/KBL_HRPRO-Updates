# Copyright (c) 2021, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.desk.form.load import get_attachments
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue


class BackgroundCheck(Document):
	def validate(self):
		attachments = self.get_attachments()
		email_args = {
			"recipients": 'mohamedyousuf.e@groupteampro.com',
			"subject": 'test',
			"message": 'test',
			"attachments": [attachments]
				}
		frappe.errprint(attachments)
		enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
	
	def get_attachments(self):
		attachments = get_attachments(self.doctype, self.name)
		# attachments = [d.file_name for d in get_attachments(self.doctype, self.name)]
		# attachments.append(frappe.attach_print(self.doctype, self.name, doc=self))
		return attachments
