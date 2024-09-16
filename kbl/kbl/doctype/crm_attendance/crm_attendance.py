# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CRMAttendance(Document):
	def on_submit(self):
		if self.workflow_state == "Approved":
			att = frappe.get_doc("Attendance",{"name":self.attendance})
			att.status = self.status
			att.save(ignore_permissions = True)
			att.docstatus = 1
			frappe.db.set_value("Attendance",self.attendance,"workflow_state","Approved by HR")
			frappe.db.commit()
