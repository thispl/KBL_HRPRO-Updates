# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmailCommunication(Document):
	pass
@frappe.whitelist()
def email_communication(designation,template,content,region):
    names = []
    try:
        data = json.loads(designation)
    except json.JSONDecodeError:
        frappe.log_error("Invalid JSON format for 'designation'")
        return ""
    for item in data:
        if not isinstance(item, dict) or 'designation' not in item:
            frappe.log_error("Invalid data format for 'designation'")
            continue
        designation_value = item['designation']
        employees = frappe.get_all("Employee", filters={"status": "Active", "designation": designation_value}, fields=["user_id"])        # Append employee names to 'names' list
        for employee in employees:
            names.append(employee.user_id)
    emailid= names
    
    frappe.sendmail(
        recipients=emailid,
        cc=['evasengupta@kblservices.in','hrops@kblservices.in '],
        subject=template,
        message="""
           <b> Dear Sir/Mam,<b><b>{}
           Thanks & Regards,<br>
                    HR Department,<br>
                    KBL Services Ltd, Bengaluru<br>
                    *This email has been automatically generated. Please do not reply*
                """.format(content)
    )
    region_employee(region,template,content)

import json
@frappe.whitelist()
def region_employee(region,template,content):
    names = []
    try:
        data = json.loads(region)
    except json.JSONDecodeError:
        frappe.log_error("Invalid JSON format for 'region'")
        return ""
    for item in data:
        if not isinstance(item, dict) or 'region' not in item:
            frappe.log_error("Invalid data format for 'region'")
            continue
        designation_value = item['region']
        employees = frappe.get_all("Employee", filters={"status": "Active", "region": designation_value}, fields=["user_id"])        # Append employee names to 'names' list
        for employee in employees:
            names.append(employee.user_id)
    emailid= names
    
    frappe.sendmail(
        recipients=emailid,
        cc='',
        subject=template,
        message="""
           <b> Dear Sir/Mam,<b><b>{}
           Thanks & Regards,<br>
                    HR Department,<br>
                    KBL Services Ltd, Bengaluru<br>
                    *This email has been automatically generated. Please do not reply*
                """.format(content)
    )
 