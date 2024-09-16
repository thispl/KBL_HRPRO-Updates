from cgi import print_environ
import mysql.connector 
import requests,json
from datetime import date
from datetime import time,datetime
import frappe

@frappe.whitelist()
def bgv_api(doc_id,jname):
	mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="Pa55w0rd@",
	database="_f5f73ab0f0fc7696"
	)

	mycursor = mydb.cursor(dictionary=True)
	query = "SELECT * FROM `tabJob Applicant` where email_id = %s"
	mycursor.execute(query, (doc_id,))  
	attlog = mycursor.fetchall()
	frappe.errprint(attlog)
	if attlog:
		for a in attlog:
			url = "https://erp.teamproit.com//api/method/teampro.www.kbl_bg_entry.new_kbl_bg?email=%s&phone=%s&gender=%s&address=%s&dob=%s&father=%s&name=%s&regno=%s&degree=%s&special=%s&cname=%s&uname=%s&courseperiod=%s&yearofpass=%s&degcert=%s&experience=%s&employer=%s&addandcont=%s&empcode=%s&emptype=%s&empperiod=%s&empdesig=%s&ctcdrawn=%s&appointment=%s&reason=%s&ref1=%s&cont1=%s&des1=%s&ref2=%s&cont2=%s&des2=%s&address1=%s&city=%s&state=%s&aadhar=%s&resume=%s" % (a['email_id'],a['phone_number'],a['gender'],a['address_3'],a['date_of_birth'],a['father_husband_name'],a['applicant_name'],a['register_number'],a['degree'],a['specialization'],a['college_name'],a['university_name'],a['course_period'],a['year_of_passed'],a['puc_'],a['work_experience'],a['employer_name'],a['address_and_contact'],a['employee_code'],a['employment_type'],a['period_of_employment'],a['previous_designation'],a['ctc'],a['appointment_letter'],a['reason_for_leaving'],a['reference_name_1'],a['contact_of_ref1'],a['designation_of_ref1'],a['reference_name_2'],a['contact_of_ref2'],a['designation_of_ref2'],a['address_'],a['city'],a['state_and_country'],a['aadhar_id'],a['resume_attachment'])
			frappe.errprint("created")
			headers = { 'Content-Type': 'application/json','Authorization': 'token daa4a43f429c844:322158936fa8302'}
			response = requests.request('GET',url,headers=headers,verify=False)
			res = json.loads(response.text)
	bg_entry_kbl(jname)
	return "Ok"
		   
@frappe.whitelist()
def bg_entry_kbl(name):
	frappe.errprint(name)
	doc=frappe.get_doc("Job Applicant",name)
	bg = frappe.new_doc("BG Entry Form")
	bg.employee_name=doc.applicant_name
	bg.address=doc.address_3
	bg.gender=doc.gender
	bg.date_of_birth=doc.date_of_birth
	bg.email_id=doc.email_id
	bg.fathers_name=doc.father_husband_name
	bg.contact_number=doc.phone_number
	bg.document_required=doc.resume_attachment
	bg.register_no_id_no=doc.register_number
	bg.college_name=doc.college_name
	bg.university_name=doc.university_name
	bg.degree=doc.degree
	bg.specialization=doc.specialization
	bg.course_period=doc.course_period
	bg.year_of_passed=doc.year_of_passed
	bg.education_document_required=doc.puc_
	bg.experience=doc.work_experience
	bg.employment_check=doc.employer_name
	bg.address_and_contact_details=doc.address_and_contact
	bg.employee_code=doc.employee_code
	bg.employment_type=doc.employment_type
	bg.period_of_employment=doc.period_of_employment
	bg.designation=doc.previous_designation
	bg.ctc_drawn=doc.ctc
	bg.documents_required=doc.appointment_letter
	bg.data_32=doc.reason_for_leaving
	bg.data_33=doc.reference_name_1
	bg.data_34=doc.contact_of_ref1
	bg.data_35=doc.designation_of_ref1
	bg.reference_name_2=doc.reference_name_2
	bg.contact_2=doc.contact_of_ref2
	bg.designation_2=doc.designation_of_ref2
	bg.criminal_check_address=doc.address_
	bg.city=doc.city
	bg.state_and_country=doc.state_and_country
	bg.criminal_check_document_required=doc.aadhar_id
	bg.name_as_in_proof=doc.applicant_name
	bg.date_of_birth_as_in_proof=doc.date_of_birth
	bg.father_name_as_in_proof=doc.father_husband_name
	bg.scanned_document_required=doc.aadhar_id
	bg.insert()
	bg.save()
