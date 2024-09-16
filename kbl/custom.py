import frappe
from frappe import throw,_
from frappe.utils import date_diff, add_months, today,nowtime,nowdate, format_date, add_days
import datetime
import asyncio
import datetime
import time
import frappe
from frappe.utils import add_days
from datetime import date, datetime,timedelta
from frappe import throw, _
from frappe.exceptions import ValidationError
from frappe.utils import add_years, getdate,add_days
from dateutil.relativedelta import relativedelta
import math
from datetime import datetime, time
from datetime import datetime, timedelta
import calendar
from datetime import datetime


def update_website_context(context):
    context.update(dict(
        splash_image = '/files/kbl_logo.png'
    ))
    return context

@frappe.whitelist()
def create_employee_onboarding(doc,method):
    if doc.job_applicant:
        emp_onboarding = frappe.new_doc('Employee Onboarding')
        emp_onboarding_template = frappe.get_all('Employee Boarding Activity',{'parent':"HR-EMP-ONT-00003"},['activity_name'])
        emp_onboarding.update({
            "job_applicant": doc.job_applicant,
            "employee_name":doc.employee_name,
            "employee":doc.name,
            "boarding_status":"In Process",
            "job_offer": frappe.get_value("Job Offer",{'job_applicant':doc.job_applicant},['name']),
            "employee_onboarding_template": "HR-EMP-ONT-00003"
        })
        for activity in emp_onboarding_template:
            emp_onboarding.append('activities', {
                "activity_name": activity.activity_name
            })
        emp_onboarding.save(ignore_permissions=True)

# @frappe.whitelist()
# def create_user(doc,method):
# 	frappe.db.set_value('Joining Form',doc.name,'date',today())
# 	frappe.db.set_value('Joining Form',doc.name,'nominated_date',today())
# 	frappe.db.set_value('Job Applicant',doc.name,'date_1',today())
# 	from frappe.utils import random_string
# 	password = random_string(8)
# 	candidate_name = doc.applicant_name
# 	email_id = doc.email_id
# 	phone_number = doc.phone_number
# 	position_applied_for = doc.job_title
# 	user = frappe.new_doc("User")
# 	user.email = email_id
# 	user.first_name = candidate_name
# 	user.send_welcome_email = 0
# 	user.user_type = 'System User'
# 	user.module_profile = 'Job Applicant'
# 	user.role_profile_name = 'Job Applicant'
# 	user.new_password = password
# 	user.save(ignore_permissions=True)
# 	frappe.db.commit()
# 	add_arole(email_id)
# 	# add_user_permission(email_id,doc.name)
# 	send_welcome_mail(email_id,candidate_name,password)
    
@frappe.whitelist()
def add_arole(email):
    role=frappe.db.get_all('Has Role',fields=['*'],filters={'parent':email,'role':'Job Applicant'})
    if not role:
        result= frappe.get_doc({
            "doctype": "Has Role",
            "parent": email,
            "parentfield": "roles",
            "parenttype": "User",
            "role": "Job Applicant"
            }).insert()
    doc = frappe.get_doc('User',email)
    doc.save(ignore_permissions=True)
    frappe.db.commit()

@frappe.whitelist()
def add_user_permission(email,job_applicant):
    frappe.errprint(job_applicant)
    user_permission = frappe.db.exists('User Permission',{'user':email,'allow':'Job Applicant','for_value':job_applicant})
    if not user_permission:
        result= frappe.get_doc({
            "doctype": "User Permission",
            "user": email,
            "allow": "Job Applicant",
            "for_value": job_applicant,
            "apply_to_all_doctypes": 1
            }).insert()

# @frappe.whitelist()
# def send_welcome_mail(email,candidate_name,password):
# 	template = 'job_applicant_created'
# 	args = {
# 		"site_url":frappe.utils.get_url(),
# 		"full_name":candidate_name,
# 		"email_id":email,
# 		"password":password
# 	}
# 	frappe.sendmail(recipients=[email],
# 		template=template,
# 		args=args,
# 		subject=_('Job Applicant Login Creation'))

    
@frappe.whitelist()
def update_user(doc,method):
    
    if doc.user_id:
        user = frappe.get_doc('User',doc.user_id)
        user.role_profile_name = 'Employee'
        user.username = doc.name
        user.save(ignore_permissions=True)
        frappe.db.commit()

@frappe.whitelist()
def block_attendance(attendance_date,employee):
    # attendance_date = datetime.strptime(attendance_date,"%Y-%m-%d").date()
    employee_designation = frappe.get_value("Employee",{"name":employee},"designation")
    blocked_date = frappe.db.get_single_value('Block Attendance', 'block_date')
    blocked_designation = frappe.db.get_single_value('Block Attendance', 'designation')
    if employee_designation == blocked_designation and attendance_date == blocked_date:
        frappe.errprint("blocked")
        return 'Blocked'

@frappe.whitelist()
def att_time_restriction(attendance_date,employee):
    if frappe.session.user != "nandan.mn@gmail.com" or frappe.session.user != "madhavishanbogh143@gmail.com":
        from frappe.utils import add_to_date
        time = nowtime()
        emp_shift = frappe.db.get_value('Employee',{"name":employee},'shift_type')
        current_date = datetime.today()
        attendance_date = datetime.strptime(attendance_date,'%Y-%m-%d')
        previous_date = current_date + timedelta(days=-1)
        if attendance_date.date() <= previous_date.date():
            return 'Previous Day'
        if emp_shift == 'Night Shift':
            if datetime.strptime(time,'%H:%M:%S.%f').time()  > datetime.strptime('21:30', '%H:%M').time():

                return 'Late Entry'
        else:  
            if datetime.strptime(time,'%H:%M:%S.%f').time()  > datetime.strptime('11:30', '%H:%M').time():        
        
                return "Late"
            
@frappe.whitelist()
def update_previous_leave_allocation_manually():
    employee = frappe.db.sql(""" select date_of_joining,name from `tabEmployee` where status = 'Active' """,as_dict=True)
    current_date = date.today()
    for i in employee:
        d = add_months(i.date_of_joining,1)
        if d <= current_date:
            print(d)
            print(i.name)
            exist = frappe.db.exists("Leave Allocation",{"leave_type":"Privilege Leave","employee":i.name,"docstatus":1})
            if not exist:
                new_all = frappe.new_doc("Leave Allocation")
                new_all.employee = i.name
                new_all.new_leaves_allocated = 1.5
                new_all.leave_type = "Privilege Leave"
                new_all.company =frappe.db.get_value("Employee",i.name,["company"])
                new_all.from_date = date.today()
                new_all.to_date = date.today().replace(month=12, day=31)
                new_all.save(ignore_permissions=True)
                new_all.submit()
            else:
                priv = frappe.get_doc("Leave Allocation",exist)
                priv.new_leaves_allocated = 1.5
                priv.total_leaves_allocated = priv.total_leaves_allocated + priv.new_leaves_allocated
                priv.save(ignore_permissions=True)




@frappe.whitelist()
def create_sick_leave_allocation(doc, method):
    date_of_joining = doc.date_of_joining    
    if isinstance(date_of_joining, str):
        try:
            year, month, day = map(int, date_of_joining.split('-'))
        except ValueError:
            frappe.throw("Date of joining is not in the expected format YYYY-MM-DD")
    elif isinstance(date_of_joining, datetime.datetime):
        year, month, day = date_of_joining.year, date_of_joining.month, date_of_joining.day
    else:
        frappe.throw("Date of joining is neither a string nor a datetime object")   
    att_date_obj = datetime.datetime(year, month, day)
    joining_date = att_date_obj.date()
    joining_month = att_date_obj.month
    joining_year = att_date_obj.year + 1
    to_date = joining_date.replace(year=joining_year) 
    months_remaining = 12 - joining_month + 1
    total_leave_days = (months_remaining / 12) * 7
    total_leave_days = math.ceil(total_leave_days)
    if not frappe.db.exists("Leave Allocation", {
        "employee": doc.employee_number,
        "leave_type": "Sick Leave",
        "docstatus": 1,
        "from_date": doc.date_of_joining,
        "to_date": to_date
    }):
        sla = frappe.new_doc("Leave Allocation")
        sla.employee = doc.employee_number
        sla.employee_name = doc.first_name
        sla.leave_type = "Sick Leave"
        sla.from_date = doc.date_of_joining
        sla.to_date = to_date
        sla.total_leaves_allocated = 12
        sla.new_leaves_allocated = 12
        sla.insert(ignore_permissions=True)
        sla.submit()


@frappe.whitelist()
def create_privilege_leave_allocation(doc, method):
    date_of_joining = doc.date_of_joining
    if isinstance(date_of_joining, str):
        year, month, day = map(int, date_of_joining.split('-'))
    elif isinstance(date_of_joining, datetime.datetime):
        year, month, day = date_of_joining.year, date_of_joining.month, date_of_joining.day
    # year, month, day = map(int, doc.date_of_joining.split('-'))
    att_date_obj = datetime.datetime(year, month, day)
    joining_date=att_date_obj.date() 
    # joining_date = datetime.strptime(doc.date_of_joining, '%Y-%m-%d')
    joining_month = att_date_obj.month
    joining_year = att_date_obj.year + 1
    to_date = joining_date.replace(year=joining_year)
    months_remaining = 12 - joining_month + 1
    total_leave_days = (months_remaining / 12) * 7
    total_leave_days = math.ceil(total_leave_days)
    if not frappe.db.exists("Leave Allocation", {
        "employee": doc.employee_number,
        "leave_type": "Privilege Leave",
        "docstatus": 1,
        "from_date": doc.date_of_joining,
        "to_date": to_date
    }):
        sla = frappe.new_doc("Leave Allocation")
        sla.employee = doc.employee_number
        sla.employee_name = doc.first_name
        sla.leave_type = "Privilege Leave"
        sla.from_date = doc.date_of_joining
        sla.to_date = to_date
        sla.total_leaves_allocated = 18
        sla.is_carry_forward=1
        sla.new_leaves_allocated = 18
        sla.insert(ignore_permissions=True)

        # Submit the newly created document
        sla.submit()

@frappe.whitelist()
def before_submit(doc, method):
    # Calculate available leave balance for the employee
    employee = frappe.get_doc("Employee", doc.employee)
    leave_balance = get_leave_balance(employee, doc.leave_type)

    # Check if a medical certificate is provided
    if not doc.get("attache_medical_certificate"):
        # Check if sufficient balance is available
        if leave_balance >= doc.total_leave_days:
            doc.leave_type = "Earned Leave"  # Set leave type to Earned Leave
        else:
            doc.leave_type = "Leave Without Pay"  # Set leave type to Leave Without Pay
    else:
        doc.leave_type = "Sick Leave"  # Set leave type to Sick Leave if medical certificate is provided

    # Check if sick leave is being accrued within the same calendar year
    today = frappe.utils.today()
    leave_year = doc.from_date.year
    if leave_year == today.year:
        doc.sick_leave_accrued = True
    else:
        doc.sick_leave_accrued = False

def get_leave_balance(employee, leave_type):
    # Query leave allocation records for the given employee and leave type
    leave_allocations = frappe.get_all("Leave Allocation",
                                       filters={"employee": employee.name, "leave_type": leave_type},
                                       fields=["total_leaves_allocated", "leaves_taken"])

    # Calculate available leave balance
    total_allocated = sum([allocation.total_leaves_allocated for allocation in leave_allocations])
    total_taken = sum([allocation.leaves_taken for allocation in leave_allocations])
    balance = total_allocated - total_taken

    return balance

# @frappe.whitelist()
# def lead_create(lead):
# 	new_lead = frappe.get_doc("Visit Report",{"name":lead},["*"])
# 	if new_lead.leadcustomer == "Lead":
# 		new_doc = frappe.new_doc('Lead')
# 		new_doc.lead_name = new_lead.person_name  
# 		new_doc.email_id = new_lead.email_address
# 		new_doc.lead_owner = new_lead.lead_owner
# 		new_doc.salutation = new_lead.salutation
# 		new_doc.designation = new_lead.designation
# 		new_doc.gender = new_lead.gender
# 		new_doc.save(ignore_permissions=True)
    
# 	elif new_lead.leadcustomer == "Customer":
# 		doc_new = frappe.new_doc('Customer')
# 		doc_new.customer_name = new_lead.person_name  
# 		doc_new.customer_type = new_lead.type_name
# 		doc_new.customer_group = new_lead.customer_group
# 		doc_new.salutation = new_lead.salutation
# 		doc_new.territory = new_lead.territory_name
# 		doc_new.gender = new_lead.gender
# 		doc_new.save(ignore_permissions=True)
    

# @frappe.whitelist()
# def inactive_employee(doc,method):
# 	if doc.status=="Active":
# 		if doc.relieving_date:
# 			throw(_("Please remove the relieving date for the Active Employee."))


@frappe.whitelist()
def visit_report(doc,method):
    data = '' 
    data += 'Dear Sir/Mam,<br>Kindly Check The Below Details For Visit Report <br><table class="table table-bordered" border="1">'
    data += '<tr><td>Visit Type</td><td>%s</td></tr>' % doc.visit_type
    data += '<tr><td>Type</td><td>%s</td></tr>' % doc.type
    data += '<tr><td>Visit To</td><td>%s</td></tr>' % doc.visit_to or doc.leadcustomer
    data += '<tr><td>Customer/Lead</td><td>%s</td></tr>' % doc.party or doc.person_name
    data += '<tr><td>Email</td><td>%s</td></tr>' % doc.email_address or doc.email_id
    data += '<tr><td>Address</td><td>%s</td></tr>' % doc.customer_address or doc.new_address
    data += '<tr><td>Status</td><td>%s</td></tr>' % doc.status_update
    data += '<tr><td>Next Action</td><td>%s</td></tr>' % doc.next_action
    data += '<tr><td>Next Follow Up By</td><td>%s</td></tr>' % doc.follow_up_owner
    data += '<tr><td>Next Follow Up On</td><td>%s</td></tr>' % doc.date_of_follow_up
    data += '<tr><td>Remarks</td><td>%s</td></tr>' % doc.remarks
    data += '<tr><td>Visit Address</td><td>%s</td></tr>' % doc.address
    data += '</table>'
    recipient = [email.strip() for email in doc.sales_manager_email.split(',')]

    frappe.sendmail(
        recipients=recipient,
        subject=('Visit Details'),
        header=('Visit Report'),
        message=data
    )


# @frappe.whitelist()
# def visit_report(doc,method):
#     # visits = frappe.get_all("Visit Report", ["*"])

#     data = """
#         <html>
#         <head>
#             <style>
#                 table {
#                     border-collapse: collapse;
#                     width: 100%;
#                 }
#                 th, td {
#                     border: 1px solid black;
#                     padding: 8px;
#                     text-align: left;
#                 }
#             </style>
#         </head>
#         <body>
#             <p>Dear Sir/Mam,</p>
#             <p>Kindly Check The Below Details For Visit Report</p>
#             <table>
#                 <tr>
#                     <th>Visit Type</th>
#                     <th>Type</th>
#                     <th>Visit To</th>
#                     <th>Customer/Lead</th>
#                     <th>Status</th>
#                     <th>Next Action</th>
#                     <th>Next Follow Up By</th>
#                     <th>Next Follow Up On</th>
#                     <th>Remarks</th>
#                     <th>Visit Address</th>
#                 </tr>
#     """

#     # for visit in doc:
#     data += """
#         <tr>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#             <td>{}</td>
#         </tr>
#     """.format(
#         doc.get("visit_type"),
#         doc.get("type"),
#         doc.get("visit_to"),
#         doc.get("party"),
#         doc.get("status_update"),
#         doc.get("next_action"),
#         doc.get("follow_up_owner"),
#         doc.get("date_of_follow_up"),
#         doc.get("remarks"),
#         doc.get("address"),
#     )

#     data += """
#             </table>
#         </body>
#         </html>
#     """

#     frappe.sendmail(
#         recipients=['sahayasterwin17@gmail.com', 'sahayasterwin.a@groupteampro.com'],
#         subject='Visit Details',
#         message=data,
#     )

@frappe.whitelist()
def update_employee_no(name,employee_number):
    emp = frappe.get_doc("Employee",name)
    emps=frappe.get_all("Employee",{"status":"Active"},['*'])
    for i in emps:
        if emp.employee_number == employee_number:
            pass
        elif i.employee_number == employee_number:
            frappe.throw(f"Employee Number already exists for {i.name}")
        else:
            frappe.db.set_value("Employee",name,"employee_number",employee_number)
            frappe.rename_doc("Employee", name, employee_number, force=1)
            return employee_number


@frappe.whitelist()
def crm_att(doc,method):
    if doc.sales_person == 1:
        new_doc = frappe.new_doc('CRM Attendance')
        new_doc.employee = doc.employee  
        new_doc.emp_name = doc.employee_name
        new_doc.company = doc.company
        new_doc.date = doc.attendance_date
        new_doc.department = doc.department
        new_doc.status = doc.status
        new_doc.attendance = doc.name
        new_doc.save(ignore_permissions=True)

from frappe.utils import now_datetime
from erpnext.hr.doctype.leave_allocation.leave_allocation import OverlapError

def check_overlap(leave_allocation, check_date):
    # Your implementation here
    pass


@frappe.whitelist()
def create_privilege_leave():
    # Fetch all active employees
    employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
    current_date = datetime.now().date()
    last_day_of_month = datetime(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]).date()

    for emp in employees:
        doj = emp.date_of_joining

        existing_allocations = frappe.get_all(
            "Leave Allocation",
            filters={
                "employee": emp.name,
                "leave_type": "Privilege Leave",
                "to_date": "31-12-2024",
                "docstatus": 1,  # Submitted documents
            },
            fields=["name", "new_leaves_allocated"]
        )

        if existing_allocations:
            for allocation in existing_allocations:
                try:
                    allocation_doc = frappe.get_doc("Leave Allocation", allocation["name"])
                    allocation_doc.new_leaves_allocated += 1.5
                    allocation_doc.save(ignore_permissions=True)
                    allocation_doc.submit()
                except OverlapError as e:
                    # Log the error and continue to the next iteration
                    frappe.log_error(f"OverlapError: {e}", "create_privilege_leave")
                    continue
                except Exception as e:
                    # Re-raise the exception if it's not an OverlapError
                    raise
        else:
            # Create a new "Privilege Leave" allocation if not exists
            la = frappe.new_doc("Leave Allocation")
            la.employee = emp.name
            la.leave_type = "Privilege Leave"
            la.new_leaves_allocated = 1.5
            la.from_date = doj
            la.to_date = last_day_of_month

            try:
                la.save(ignore_permissions=True)
                la.submit()
                print('New Leave Allocation created successfully')
            except OverlapError as e:
                # Log the error and continue to the next iteration
                frappe.log_error(f"OverlapError: {e}", "create_privilege_leave")
                continue
            except Exception as e:
                # Re-raise the exception if it's not an OverlapError
                raise

from datetime import datetime, time
@frappe.whitelist()
def validate_block_att(doc,method):
    if doc.is_new():
        from datetime import datetime, timedelta
        frappe.errprint("Hello1")
        employee = doc.employee
        attendance_date = doc.attendance_date
        emp_id = doc.employee
        frappe.errprint(emp_id)
        emp = frappe.get_doc("Employee", emp_id)
        shift_type = frappe.db.get_value("Employee", {'name': emp_id}, ['shift_type'])
        etime = frappe.db.get_value("Shift Type", {"name": shift_type}, ['checkin_end_time'])
        ltime_str = frappe.db.get_value("Shift Type", {"name": shift_type}, ['checkin_late'])

        if ltime_str:
            if isinstance(ltime_str, timedelta):
                frappe.errprint("if1")
                ltime_time = (datetime.min + ltime_str).time()
            else:
                frappe.errprint("else1")
                ltime_time = datetime.strptime(ltime_str, '%H:%M:%S').time()

        if etime:
            if isinstance(etime, timedelta):
                frappe.errprint("if2")
                etime_time = (datetime.min + etime).time()
            else:
                frappe.errprint("else2")
                etime_time = datetime.strptime(etime, '%H:%M:%S').time()

        # if isinstance(attendance_date, datetime.date):
        #     attendance_date_str = attendance_date.strftime('%Y-%m-%d')
        # elif isinstance(attendance_date, str):
        #     attendance_date_str = attendance_date

        # attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d')

        # formatted_date = attendance_date_obj.strftime('%d-%m-%Y')
        if isinstance(attendance_date, str):
            attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        current_date = datetime.today().date()
        current_time = datetime.now().time()
        restriction=frappe.db.get_value("Employee", {'user_id': frappe.session.user}, ['no_restrictions'])
        if restriction == 0:
            if shift_type:
                if attendance_date == current_date and current_time > ltime_time:
                    frappe.throw('Attendance cannot be marked one and half hour after the shift start timing')
                elif attendance_date < current_date:
                    frappe.throw('Attendance cannot be marked for past dates')
                elif attendance_date == current_date and etime_time <= current_time <= ltime_time:
                    Late = 1
                    doc.late_entry=Late	
                    doc.save()
                    frappe.msgprint('Attendance marked one hour after shift start timing will be marked as Late.')
            else:
                if emp.designation != 'Data Entry Operator':
                    if attendance_date == datetime.today().date():
                        if time(10, 30) <= datetime.now().time() <= time(11, 59):
                            Late = 1
                            doc.late_entry=Late	
                            doc.save()
                            frappe.msgprint('Attendance marked between 10.30AM and 11:59AM will be marked as Late.')	
                        elif datetime.now().time() > time(11, 59):
                            frappe.throw('Attendance cannot be marked after 11:59AM.')
                    elif attendance_date() < datetime.today().date():
                        frappe.throw('Attendance cannot be marked for past dates.')
        # else:
        #     frappe.errprint("else part")
            
@frappe.whitelist
def att_restriction():
    shift_time=frappe.db.get_value("Shift Type",{"checkin_start_time"('<=',nowdate)},["name"])


@frappe.whitelist()
def contract_end_mail():
    start_date = nowdate()
    end_date = add_days(nowdate(), 30)
    count = 0
    hr_users = frappe.get_all("User", {"role": ('in', ["HR User", "HR Manager"]), "enabled": 1}, ["email"])
    hr_user_emails = [user["email"] for user in hr_users]  
    data = ""
    data += '<table border="1" width="100%" style="border-collapse: collapse;text-align: center;" ><tr style="background-color: #be83d4;color:white;"><b><td width="5%">S.NO</td><td width="10%">EMP ID</td><td width="20%">EMPLOYEE NAME</td><td width="20%">DEPARTMENT</td><td width="20%">DESIGNATION</td><td width="20%">CONTRACT END DATE</td><td width="5%">DAYS LEFT</td></b></tr>'
    
    exp_employees = frappe.db.sql("""
        SELECT name, employee_name, designation, department, contract_end_date 
        FROM `tabEmployee` 
        WHERE contract_end_date BETWEEN %s AND %s
    """, (start_date, end_date), as_dict=True)
    
    hod_mail = []
    
    for emp in exp_employees:
        count += 1
        hod = frappe.db.get_value("Employee", {"name": emp.name}, "reports_to")
        hod_email = frappe.db.get_value("Employee", {"name": hod}, "user_id")
        if hod_email:
            hod_mail.append(hod_email)
        remaining_days = date_diff(emp.contract_end_date, start_date)
        data += '<tr><td>%s</td><td style="text-align: left;">%s</td><td style="text-align: left;">%s</td><td style="text-align: left;">%s</td><td style="text-align: left;">%s</td><td style="text-align: left;">%s</td><td>%s</td></tr>' % (count, emp.name, emp.employee_name, emp.designation, emp.department, emp.contract_end_date or ' ', remaining_days)
    
    data += '</table>'
    
    frappe.sendmail(
        recipients=hr_user_emails,
        cc=hod_mail,  
        subject='Contract End Details - {}'.format(nowdate()),
        message="""
            Dear Sir/Madam,<br>
            Kindly find the below List along with its Contract end Details:<br>
            {} <br>
            Thanks & Regards,<br>
            HR Department,<br>
            KBL Services Ltd, Bengaluru<br>
            *This email has been automatically generated. Please do not reply*
        """.format(data)
    )



# @frappe.whitelist()
# def mail_alert_for_contract_end_date():
#     job = frappe.db.exists('Scheduled Job Type', 'contract_end_alert')
#     if not job:
#         sjt = frappe.new_doc("Scheduled Job Type")
#         sjt.update({
#             "method": 'kbl.custom.contract_end_mail',
#             "frequency": 'Cron',
#             "cron_format": '00 09 * * *'
#         })
#         sjt.save(ignore_permissions=True)
@frappe.whitelist()
def mail_alert_for_contract_end_date():
    job = frappe.db.exists('Scheduled Job Type', 'contract_end_alert')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'kbl.custom.contract_end_mail',
            "frequency": 'Cron',
            "cron_format": '00 09 * * *'
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def update_relieving_date(date,employee,posting_date):
    frappe.db.set_value("Employee",employee,"relieving_date",date)
    frappe.db.set_value("Employee",employee,"exit_type","Resigned")
    frappe.db.set_value("Employee",employee,"resignation_letter_date",posting_date)

# @frappe.whitelist()
# def update_warning_count(doc,method):
#     document = frappe.db.exists("Warning Letter",{"employee",doc.employee})
#     if not document:
#         count = frappe.db.sql(""" SELECT COUNT(warning) AS count FROM `tabWarning Letter` WHERE employee=%s ORDER BY creation DESC """, (doc.employee,), as_dict=True)
#         if count:
#             warning_count = count[0]['count'] + 1
#             frappe.db.set_value("Warning Letter", doc.name, "warning", warning_count)

# @frappe.whitelist()
# def warning_letter_mail(name,issue,user_id=None):
# 	table_html = ''
# 	si_list = frappe.db.sql("""SELECT * FROM `tabWarning Letter` WHERE name = %s""", (name), as_dict=True)
# 	if si_list:
# 		header = f"""<p style = text-align:center>Warning Letter</p>"""
# 		regards = "Thanks & Regards"
# 		table_html += '<table>'
# 		for si in si_list:
# 			img=frappe.db.get_value("File",{'name':"1a5d2a742f"},['file_url'])
# 			depart_head = si.department_head
# 			ksl_head = si.ksl_head
# 			table_html += '<tr><img src="img"> </tr>'
# 			table_html += '<tr><b>From</b></tr>'
# 			table_html += '<tr><b>Regd. Office:</b>Hafeeza Chambers, No.111/3 (old No.74),</tr>'
# 			table_html += '<tr>3rd Floor, A-Wing, K H Road, Bengaluru -560027,</tr>'
# 			table_html += '<tr><b>Ph</b> : +918041212452 / 41251494,</tr>'
# 			table_html += '<tr><b>Email</b> : info@kblservices.in,</tr>'
# 			table_html += '<tr><b>CIN</b> : U74900KA2020PLC135108</tr>'
# 			table_html += '<tr><b><br>To</b></tr>'
# 			table_html += '<tr>{},</tr>'.format(si.employee_name)
# 			table_html += '<tr><b>Employee ID</b>{},</tr>'.format(si.employee)
# 			table_html += '<tr><b>Designation</b>{},</tr>'.format(si.designation)
# 			table_html += '<tr><b>S/O Mr.</b>{},</tr>'.format(si.father_name)
# 			table_html += '<tr>{}</tr>'.format(si.address)
# 			table_html += '<tr><b><br>Sir,</b></tr>'
# 			table_html += '<tr><b><br>Subject: {},</tr>'.format(issue)
# 			table_html += '<tr>Ref:1)Your Appointment Letter dated{},</tr>'.format(si.doj)
# 			table_html += '<tr>2)Our letter Ref. No KSL/P/784/000005 dated {},</tr>'.format(si.posting_date)
# 			table_html += '<tr><br>{}</tr>'.format(si.mail_content)
# 			table_html += '<tr><br>With Regards</tr>'
# 			table_html += '<tr>Chandramouli Bharadwaj</tr>'
# 			table_html += '<tr>Chief Operating Officer</tr>'
            
# 		table_html += '</table><br>'
# 		subject = 'Warning Letter'
# 		frappe.sendmail(
# 			recipients=[user_id,depart_head,ksl_head],
# 			subject=subject,
# 			message=header + table_html + regards
# 		)
# 		frappe.db.set_value("Warning Letter",name,"check",1)

# @frappe.whitelist()
# def notification_Sent(doc,method):
# 	subject = 'Reg. Resignation Letter'
# 	frappe.sendmail(
# 		recipients=doc.user_id,
# 		subject=subject,
# 		message='your resignation is accepted on Date (DD:MM:YYYY) and should serve notice period as per company policy'
# 	)

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

@frappe.whitelist()
def test_contract_end_reminder():
    start_date = nowdate()
    end_date = add_days(nowdate(), 400)
    
    exp_employees = frappe.db.sql("""
        SELECT name, employee_name, designation, department, contract_end_date
        FROM `tabEmployee`
        WHERE contract_end_date BETWEEN %s AND %s 
        AND employee_number = 'KSL0531'
        AND status = 'Active'
    """, (start_date, end_date), as_dict=True)

    for emp in exp_employees: 
        hod = frappe.db.get_value("Employee", {"name": emp.name}, ["reports_to"])
        hod_mail = frappe.db.get_value("Employee", {"name": hod}, ["user_id"]) if hod else None
        # emp_mail = frappe.db.get_value("Employee", {"name": emp.name}, ["user_id"])
        # hod_name = frappe.db.get_value("Employee", {"name": hod}, ["employee_name"]) 
        print(hod_mail)
        
        attachments = None
        if emp.designation == 'Business Process Associate':
            attachments = [frappe.attach_print("Employee", emp.name, file_name="Business Process Associate Contract Renewal Letter", print_format="Business Process Associate Contract Renewal")]
        elif emp.designation == 'Customer Support Associate':
            attachments = [frappe.attach_print("Employee", emp.name, file_name="Customer Support Associate Contract Renewal Letter", print_format="Customer Support Associate-Contract Renewal")]
        elif emp.designation == 'CASA Marketing Associate':
            attachments = [frappe.attach_print("Employee", emp.name, file_name="CASA Marketing Associate Contract Renewal Letter", print_format="CASA Marketing Associate Contract Renewal")]
        elif emp.designation == 'Data Entry Operator':
            attachments = [frappe.attach_print("Employee", emp.name, file_name="Data Entry Operator Contract Renewal Letter", print_format="Data Entry Operator-Contract Renewal")]
        elif emp.designation == 'Direct Sales Associate-Retail':
            attachments = [frappe.attach_print("Employee", emp.name, file_name="Direct Sales Associate Retail Contract Renewal Letter", print_format="Direct Sales Associate Retail Contract Renewal")]
        elif emp.designation == 'Technical Support Officer':
            attachments = [frappe.attach_print("Employee", emp.name, file_name="Technical Support Officer Contract Renewal Letter", print_format="Technical Support Officer-Contract Renewal")]

        frappe.sendmail(
            recipients='nandini.a@groupteampro.com',
            cc='nandini.a@groupteampro.com',
            subject='Consent for Renewal of Job Contract  - {}'.format(format_date(nowdate(), "dd-MM-yyyy")),
            message="""
                Dear {},<br> <br> 
                <b>Please review the attached contract carefully, sign where indicated, and return it to the Human Resources Department to finalize the renewal process.</b> <br>
                <br> <br><br>  
                Thanks & Regards,<br>
                HR Department,<br>
                KBL Services Ltd, Bengaluru<br><br>
                **Note:** This is an automated email notification. Please do not reply to this email.
            """.format(emp.employee_name),
              attachments=attachments
        )
        print("ok")

# @frappe.whitelist()
# def mail_cron_for_test_contract_end_reminder():
#     job = frappe.db.exists('Scheduled Job Type', 'test_contract_end_reminder')
#     if not job:
#         cer = frappe.new_doc("Scheduled Job Type")
#         cer.update({
#             "method": 'kbl.custom.test_contract_end_reminder',
#             "frequency": 'Cron',
#             "cron_format": '00 09 * * *'
#         })
#         cer.save(ignore_permissions=True)

@frappe.whitelist()
def contract_end_reminder():
    start_date = nowdate()
    end_date = add_days(nowdate(),30)
    exp_employees = frappe.db.sql("""
    SELECT name, employee_name, designation, department, contract_end_date
    FROM `tabEmployee`
    WHERE contract_end_date BETWEEN %s AND %s
    AND status = 'Active'
""", (start_date, end_date), as_dict=True)

    for emp in exp_employees: 
        hod = frappe.db.get_value("Employee", {"name": emp.name}, ["reports_to"])
        hod_mail = frappe.db.get_value("Employee", {"name": hod}, ["user_id"]) if hod else None
        emp_mail = frappe.db.get_value("Employee", {"name": emp.name}, ["user_id"])
        hod_name = frappe.db.get_value("Employee", {"name": hod}, ["employee_name"]) 
        print (hod)
        frappe.sendmail(
                recipients=emp_mail,
                cc=hod_mail if hod_mail else [],  
                subject='Consent for Renewal of Job Contract  - {}'.format(nowdate()),
                message="""
                    Dear Sir/Madam,<br> <br> 
                    We are pleased to inform you that we are extending an offer to renew your job contract with KBL Services Ltd, for a period of one year.<br>
                    We are confident that your continued presence within our organization will further contribute to our success. Therefore, we are offering you a one-year extension of your job contract. <br>
                    By signing this letter, you acknowledge your agreement to the terms and conditions outlined in your previous Offer letter shared by us. <br>
                    Please review the attached contract carefully, sign where indicated, and return it to the Human Resources Department to finalize the renewal process. <br>
                    Should you have any questions or require further clarification regarding your renewed contract, please do not hesitate to contact the Human Resources Department. <br> 
                    We look forward to your continued contributions to KBL Services Ltd and to a mutually beneficial working relationship over the coming year. <br>
                    Thank you for your dedication and commitment. <br> <br><br>  
                    Sincerely, <br> 
                    Chandramouli Bharadwaj <br> 
                    Chief Executive Officer <br><br> 

                    I, {} hereby acknowledge my consent to the renewal of my job contract with KBL Services Ltd for a period of one year, effective from_________________. <br> <br><br>
                    [Employee Signature]<br> 
                    Date: {} <br><br>
                    I,{}, hereby acknowledge my consent to the renewal of my  reportee Mr/Ms. {} job contract with KBL Services Ltd for a period of one year, effective from ____________________. <br> <br> <br> 
                    [Employer Signature]  <br> 
                    Date: {} 



                    Thanks & Regards,<br>
                    HR Department,<br>
                    KBL Services Ltd, Bengaluru<br>
                    *This email has been automatically generated. Please do not reply*
                """.format(emp.employee_name,nowdate(),hod_name,emp.employee_name,nowdate())
            )


@frappe.whitelist()
def contract_renewal():
    start_date = nowdate()
    end_date = add_days(nowdate(),30)
    exp_employees = frappe.db.sql("""
        SELECT name, employee_name, designation, department, contract_end_date, renewal_date,date_of_joining
        FROM `tabEmployee` 
        WHERE contract_end_date BETWEEN %s AND %s
        AND status = 'Active'
    """, (start_date, end_date), as_dict=True)
    for emp in exp_employees: 
        hod = frappe.db.get_value("Employee", {"name": emp.name}, ["reports_to"])
        hod_mail = frappe.db.get_value("Employee", {"name": hod}, ["user_id"]) if hod else None
        emp_mail = frappe.db.get_value("Employee", {"name": emp.name}, ["user_id"])
        hod_name = frappe.db.get_value("Employee", {"name": hod}, ["employee_name"]) 
        print (hod)
        frappe.sendmail(
                recipients=emp_mail,
                cc=hod_mail if hod_mail else [],  
                subject='Continuation Of the Service',
                message="""
                    <b>Dear Sir/Madam,</b><br><br>
                    Mr/Ms <u><b>{}</b></u><br>
                    Emp.ID: <u><b>{}</b></u><br>
                    Designation:  <u><b>{}</b></u><br>
                    Present HQ: <b>KBL-Branch</b> <br><br>
                    Sir, <br><br>
                    Sub: Continuation of the Service in the company<br>
                    Ref: Your Appointment letter dated {}<br><br>
                    With reference to the above, your service in the company is continued as per your request, for a further period of one year on contract basis from <b>{}</b>. <br>
                    There is no change in the location of deputation, as mentioned in your appointment letter. However, you are transferable as per the requirement of the company. In case no communication is issued by us regarding continuation the contract will end on {}<br> 
                    All the other terms and conditions of the appointment letter referred above remain unaltered. <br>
                    Wish you all the best!! <br><br>
                    Regards , <br> 
                    Chandramouli Bharadwaj <br> 
                    Chief Executive Officer <br><br> 


                    Thanks & Regards,<br>
                    HR Department,<br>
                    KBL Services Ltd, Bengaluru<br>
                    *This email has been automatically generated. Please do not reply*
                """.format(emp.employee_name,emp.name,emp.designation,emp.date_of_joining,emp.renewal_date,emp.contract_end_date)
            )




# @frappe.whitelist()
# def mail_alert_for_contract_end_reminder():
#     job = frappe.db.exists('Scheduled Job Type', 'contract_end_reminder_alert')
#     if not job:
#         sjt = frappe.new_doc("Scheduled Job Type")
#         sjt.update({
#             "method": 'kbl.custom.contract_end_reminder',
#             "frequency": 'Cron',
#             "cron_format": '00 09 * * *'
#         })
#         sjt.save(ignore_permissions=True)

# @frappe.whitelist()
# def mail_alert_for_contract_renewal():
#     job = frappe.db.exists('Scheduled Job Type', 'contract_renewal_alert')
#     if not job:
#         sjt = frappe.new_doc("Scheduled Job Type")
#         sjt.update({
#             "method": 'kbl.custom.contract_renewal',
#             "frequency": 'Cron',
#             "cron_format": '00 09 * * *'
#         })
#         sjt.save(ignore_permissions=True)



@frappe.whitelist()
def get_monthly_points(doc):
    pips=frappe.db.get_all("Performance Improvement Plan",{'employee':doc.employee},['*'],order_by='month ASC')
    data = '<table border=1>'
    months = []
    points = []
    
    for p in pips:
        month = frappe.utils.get_datetime(p.month).strftime("%B-%y")
        months.append(month)
        points.append(str(p.achieved_points))
    data += '<tr>'
    for month in months:
        data += f'<td style="background-color:#808080"><b>{month}</b></td>'
    data += '</tr>'
    data += '<tr>'
    for point in points:
        data += f'<td>{point}</td>'
    data += '</tr>'
    
    data += '</table>'
    return data


@frappe.whitelist()
def get_count(doc):
    count=frappe.db.count("Performance Improvement Plan",{'employee':doc.employee})
    return count

import datetime
import calendar
@frappe.whitelist()
def get_date(doc):

    date_str = frappe.db.sql("""SELECT month FROM `tabPerformance Improvement Plan` WHERE employee = %s ORDER BY month DESC LIMIT 1""", (doc.employee,), as_dict=True)

    date = date_str[0]['month']
    month = date.month + 1
    year = date.year
    if month == 13:
        month = 1
        year += 1
    last_day = calendar.monthrange(year, month)[-1]
    new_date = str(last_day) + '-' + str(month) +'-'+str(year)
    # new_date = datetime.datetime(year, month, last_day)
    return new_date

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

# @frappe.whitelist()
# def create_cfb():
# 	job = frappe.db.exists('Scheduled Job Type', 'pip_mail')
# 	if not job:
# 		sjt = frappe.new_doc("Scheduled Job Type")
# 		sjt.update({
# 			"method" : 'kbl.custom.pip_mail',
# 			"frequency" : 'Cron',
# 			"cron_format" : '00 03 * * *'
# 		})
# 		sjt.save(ignore_permissions=True)


@frappe.whitelist()
def sal_structure(doc,method):
    # employees = frappe.get_all("Employee", {'status': 'Active'}, ["*"])
    # for employee in employees:
    #     # print(employee.name)
    #     salary_structure_assignment = frappe.db.sql("""
    #         SELECT name,salary_structure
    #         FROM `tabSalary Structure Assignment`
    #         WHERE docstatus = 1 AND employee = %s 
    #         ORDER BY from_date DESC
    #         LIMIT 1
    #     """ % frappe.db.escape(employee.name), as_dict=True)
        
    #     if salary_structure_assignment:
    #         ss_name = salary_structure_assignment[0]['salary_structure']
    #         print(ss_name)
    frappe.db.set_value("Employee", doc.employee, 'salary_structure', doc.salary_structure)


@frappe.whitelist()
def employee_creation(name='HR-APP-2024-00008'):
    frappe.errprint(name)
    edu = frappe.db.get_all('Employee Education',{'parent':name},['*'])
    for i in edu:
        print(i['course'],i['school_univ'],i['class_per'],i['university'],i['year_of_passing'])
    # doc=frappe.get_doc("Job Applicant",name)
    # joboffer=frappe.get_doc("Job Offer",{"job_applicant":name})
    # # if not joboffer:
    # #     frappe.throw(_("Create the Job Offer First"))
    # bg = frappe.new_doc("Employee")
    # bg.first_name=doc.applicant_name
    # bg.address=doc.address_3
    # bg.gender=doc.gender
    # bg.job_offer=joboffer.name
    # bg.date_of_birth=doc.date_of_birth
    # bg.fathers_name=doc.father_husband_name
    # bg.cell_number=doc.phone_number
    # bg.employee_number=doc.employee_number
    # bg.job_applicant=doc.name
    # bg.permanent_address=doc.address_
    # bg.current_address=doc.address_3
    # bg.aadhar_id1=doc.aadhar_id
    # bg.photo_attachment=doc.image
    # bg.sslc_marksheet=doc.sslc_mark_sheets
    # bg.puc_=doc.puc_
    # bg.resume_attachment=doc.resume_attachment
    # bg.upload_your_signature1=doc.upload_your_signature
    # bg.graduation1=doc.graduation_
    # bg.date_of_joining=str(doc.date_of_joining)
    # bg.pan1=doc.pan
    # bg.pg_=doc.p_g_
    # bg.address_proof_present=doc.present_proof
    # bg.address_proof_permanent=doc.permanent
    # bg.releveling_letter=doc.reliving_letter
    # bg.appointment_letter1=doc.appointment_letter
    # bg.insert()
    # bg.save()

@frappe.whitelist()
def attendance_correction():
    checkin = frappe.db.sql("""update `tabJob Applicant` set docstatus = 0 where name  = "AB - renishasiva14@gmail.com - customer-suuport-associate" """,as_dict = True)

@frappe.whitelist()
def applicant_creation(doc,method):
    candidate=doc.email_id
    cname=doc.applicant_name
    frappe.sendmail(
        recipients=candidate,
        cc='',  
        subject='Job Application Received',
        message="""
            Dear {},<br>
            Thank You for Applying. We received your job application, it is currently under review.<br><br>
            Thanks & Regards,<br>
            HR Department,<br>
            KBL Services Ltd, Bengaluru<br><br>
            <b>*This email has been automatically generated. Please do not reply*</b>
        """.format(cname)
    )

@frappe.whitelist()
def joining_form_submission(doc,method):
    candidate=doc.email
    cname=doc.first_name
    frappe.sendmail(
        recipients=candidate,
        cc='',  
        subject='Joining form is Submitted',
        message="""
            Dear {},<br>
            Your Joining form is submitted successfully.<br><br>
            Thanks & Regards,<br>
            HR Department,<br>
            KBL Services Ltd, Bengaluru<br>
            <b>*This email has been automatically generated. Please do not reply*</b>
        """.format(cname)
    )

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
    
# @frappe.whitelist()
# def joining_attachments(doc,method):
# 	frappe.errprint("HIWORLD")
# 	frappe.sendmail(
# 		recipients=doc.applicant_email,
# 		subject="Post Joining Documents",
# 		message="""<p>Dear Sir/Madam,</p>
# 			<p>Kindly find the attached documents for your reference and fill the details present in the format by taking print to complete the joining formalities.
# 			</p><br> Regards, <br>  HR Department, <br>KBL Services Ltd, Bengaluru""",
# 		now=True,
# 		attachments=[frappe.attach_print("Job Offer", doc.name,
# 			file_name="Joining Report", print_format="Joining Report"),frappe.attach_print("Job Offer", doc.name,
# 			file_name="Reporting Form", print_format="Reporting Form"),frappe.attach_print("Job Offer", doc.name,
# 			file_name="Checklist", print_format="Checklist"),frappe.attach_print("Job Offer", doc.name,
# 			file_name="Form 11", print_format="Form 11"),frappe.attach_print("Job Offer", doc.name,
# 			file_name="PF Form", print_format="PF Form"),frappe.attach_print("Job Offer", doc.name,
# 			file_name="Undertaking Form", print_format="Undertaking Form"),frappe.attach_print("Job Offer", doc.name,
# 			file_name="Employee Joining Kit", print_format="Employee Joining Kit"),frappe.attach_print("Job Applicant", doc.job_applicant,
# 			file_name="Code of Conduct",print_format="Code of Conduct"),frappe.attach_print("Job Applicant", doc.job_applicant,
# 			file_name="Code of Conduct Acknowledgement",print_format="Code of Conduct Acknowledgement"),frappe.attach_print("Job Applicant", doc.job_applicant,
# 			file_name="Attendance Register",print_format="Attendance Register"),frappe.attach_print("Job Applicant", doc.job_applicant,
# 			file_name="ID Card Request",print_format="ID Card Request"),frappe.attach_print("Job Applicant", doc.job_applicant,
# 			file_name="Gratuity Policy",print_format="Gratuity Policy")]
# 	)

@frappe.whitelist()
def job_opening_rename(doc,method):
    frappe.errprint("helloworld")
    frappe.rename_doc("Job Opening",doc.name,doc.job_title,force=1)

@frappe.whitelist()
def compoff_restriction(doc,method):
    if doc.leave_type=="Compensatory Leave":
        alloc = frappe.db.sql("""
            SELECT to_date,name 
            FROM `tabLeave Allocation` 
            WHERE employee = %s 
            AND leave_type="Compensatory Leave"
            AND %s BETWEEN from_date AND to_date 
            AND %s BETWEEN from_date AND to_date
        """, (doc.employee, doc.from_date, doc.to_date), as_dict=True)
        if alloc:
            to_date = alloc[0]['to_date']
            diff = date_diff(doc.posting_date,to_date)
            if diff > 90:
                frappe.throw(_('Compensatory Leave should be taken within the 90 days from the allocation period'))

from datetime import datetime
@frappe.whitelist()
def create_privilege_and_sick_leave_1():
    current_date = date.today()
    print(current_date)
    emp = frappe.db.sql("""
        SELECT employee_number,employee_name
        FROM `tabEmployee` 
        WHERE 
            DAY(date_of_joining) = %(day)s 
            AND MONTH(date_of_joining) < %(month)s 
            AND status = 'Active'
    """, {
        'day': current_date.day,
        'month': current_date.month
    })
    joining_year = current_date.year + 1
    to_date = current_date.replace(year=joining_year)
    print(to_date)
    for e in emp:
        print(e[1])
        if frappe.db.exists("Leave Allocation", {"employee": e[0],"leave_type": "Privilege Leave","to_date": ('<=',to_date)}):
            la = frappe.get_doc("Leave Allocation",{"employee": e[0],"leave_type": "Privilege Leave","to_date": ('<=',to_date)})
            if la.total_leaves_allocated < 18:
                la.new_leaves_allocated = la.new_leaves_allocated + 1.5
                la.total_leaves_allocated = la.total_leaves_allocated +1.5
                la.save(ignore_permissions=True)
                la.submit()   
        else:
            la = frappe.new_doc("Leave Allocation")
            la.employee = e[0]
            la.leave_type = "Privilege Leave"
            la.new_leaves_allocated = 1.5
            la.from_date = current_date
            la.to_date = to_date
            la.carry_forward=1
            la.save(ignore_permissions=True)
            la.submit()
        if frappe.db.exists("Leave Allocation", {"employee": e[0],"leave_type": "Sick Leave","to_date": ('<=',to_date)}):
            la = frappe.get_doc("Leave Allocation",{"employee": e[0],"leave_type": "Sick Leave","to_date": ('<=',to_date)})
            if la.total_leaves_allocated < 7:
                la.new_leaves_allocated = la.new_leaves_allocated + 1
                la.total_leaves_allocated = la.total_leaves_allocated +1
                la.save(ignore_permissions=True)
                la.submit()   
        else:
            la = frappe.new_doc("Leave Allocation")
            la.employee = e[0]
            la.leave_type = "Sick Leave"
            la.new_leaves_allocated = 1
            la.from_date = current_date
            la.to_date = to_date
            la.save(ignore_permissions=True)
            la.submit()
        # if not frappe.db.exists("Leave Allocation", {"employee": e[0],"leave_type": "Privilege Leave","docstatus": 1,"to_date": to_date}):
        # 	sla = frappe.new_doc("Leave Allocation")
        # 	sla.employee = e[0]
        # 	sla.employee_name = e[1]
        # 	sla.leave_type = "Privilege Leave"
        # 	sla.from_date = current_date
        # 	sla.to_date = to_date
        # 	sla.total_leaves_allocated = 1.5
        # 	sla.is_carry_forward=1
        # 	sla.new_leaves_allocated = 1.5
        # 	sla.save(ignore_permissions=True)
        # 	sla.submit()
        # else:
        # 	sla = frappe.get_doc("Leave Allocation",{"employee": e[0],"leave_type": "Privilege Leave","docstatus": 1,"to_date": to_date})
        # 	sla.employee = e[0]
        # 	sla.employee_name = e[1]
        # 	sla.leave_type = "Privilege Leave"
        # 	sla.from_date = current_date
        # 	sla.to_date = to_date
        # 	sla.total_leaves_allocated += 1.5
        # 	sla.is_carry_forward=1
        # 	sla.new_leaves_allocated += 1.5
        # 	sla.save(ignore_permissions=True)
        # 	sla.submit()
        # if not frappe.db.exists("Leave Allocation", {"employee": e[0],"leave_type": "Sick Leave","docstatus": 1,"to_date": to_date}):
        # 	sla = frappe.new_doc("Leave Allocation")
        # 	sla.employee = e[0]
        # 	sla.employee_name = e[1]
        # 	sla.leave_type = "Sick Leave"
        # 	sla.from_date = current_date
        # 	sla.to_date = to_date
        # 	sla.new_leaves_allocated = 1
        # 	sla.save(ignore_permissions=True)
        # 	sla.submit()
        # else:
        # 	sla = frappe.get_doc("Leave Allocation")
        # 	if sla.total_leaves_allocated >8:
        # 	sla.employee = e[0]
        # 	sla.employee_name = e[1]
        # 	sla.leave_type = "Sick Leave"
        # 	sla.to_date = to_date
        # 	sla.new_leaves_allocated = 1
        # 	sla.save(ignore_permissions=True)
        # 	sla.submit()
@frappe.whitelist()
def create_privilege_and_sick_leave():
    job = frappe.db.exists('Scheduled Job Type', 'create_privilege_and_sick_leave_1')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'kbl.custom.create_privilege_and_sick_leave_1',
            "frequency": 'Daily',
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def delete_att():
    ename=frappe.get_all("Employee",{'status':'Active'},['name'])
    for i in ename:
        empid=(i['name'])
        first = frappe.db.sql("""
            SELECT name,creation
            FROM `tabAttendance`
            WHERE employee=%s AND workflow_state='Draft' AND attendance_date='2024-06-01'
            ORDER BY creation ASC 
            LIMIT 1
        """,(empid))
        
        if first:
            # attendance_name = first[0][0]  
            # attendance_datetime = first[0][1]
            # print(attendance_name)
            # print(attendance_datetime)
            if not frappe.db.exists("Attendance",{'employee':empid,'workflow_state':'Pending for Sales Manager','attendance_date':'2024-06-01'}):
                print(first[0][0])
                att_time = first[0][0]
                status = frappe.db.sql("""update `tabAttendance` set workflow_state = 'Pending for Sales Manager' where name = %s""", (att_time,), as_dict=True)
        
# @frappe.whitelist()
# def appointment_attachments(doc,method):
# 	frappe.errprint("hello9")
# 	frappe.sendmail(
# 		recipients=doc.applicant_email,
# 		cc='',
# 		subject="Appointment Letter - KBL",
# 		message="""<p><b>Dear {} ,</b></p>
# 			Congratulations….<br>Please find attached the appointment letter from KBL Services Ltd.<br><br><b>Documents Required:</b><br>
# 			Marks Sheet: SSLC and PUC, Degree also convocation certificates.<br>
# 			Address Proof: Aadhar and Voter ID, if present address is different, then supporting proof like rental agreement is required.<br>
# 			ID Proof: DL and PAN Card<br>
# 			Work Experience letter.<br><br>Note: All the above documents should be separately uploaded in the link as PDFs.<br>
# 			Background Verification is a mandatory activity for all joiners. If the BGV is positive, meaning all the records, address proofs and criminal verification being done for you should come as all clear.
# 			This is mandatory to have continued employment in KBL Services Limited.<br><br>


# 			<b>Please ensure fill your BackGround Verification Form immediately using the link below.</b><br>

# 			https://erp.teamproit.com/bg-entry-form 
# 			<br><br>
# 			<br> Regards, <br>  HR Department, <br>KBL Services Ltd,Bengaluru""".format(doc.applicant_name),
# 		attachments=[frappe.attach_print("Job Offer", doc.name,file_name="Appointment letter Form", print_format="Appointment letter Form")]
# 	)


@frappe.whitelist()
def joboffer_mail(doc,method):
    frappe.enqueue(
        job_offer_email_list, 
        queue="long",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Job Offer',
        enqueue_after_commit=False,
        name=doc.name,
        branch_mail=doc.branch_mail,
        reports_to=doc.reports_to,
        applicant_email=doc.applicant_email,
        applicant_name=doc.applicant_name,
        job_applicant=doc.job_applicant,
        first_cc=doc.cc1,
        second_cc=doc.cc2,
        third_cc=doc.cc3,
        designation_name = doc.designation,


    )

# @frappe.whitelist()
# def job_offer_email_list(name,applicant_email,job_applicant,applicant_name,branch_mail,first_cc,second_cc,third_cc):
#     import time
    
#     job_offer_emails(name,applicant_email,applicant_name,job_applicant,branch_mail,first_cc,second_cc,third_cc)
#     job_offer_attachments(name,applicant_email,applicant_name,job_applicant,branch_mail,first_cc,second_cc,third_cc)

@frappe.whitelist()
def job_offer_emails(doc,method):
    frappe.errprint("Appointment")
    frappe.sendmail(
        recipients=doc.applicant_email,
        # delayed=0,
        cc=['Chandramoulibharadwaj@kblservices.in','evasengupta@kblservices.in','hrops@kblservices.in',doc.branch_mail,doc.cc1,doc.cc2,doc.cc3],
        subject="Appointment Letter - KBL",
        message="""<p><b>Dear {} ,</b></p>
            Congratulations….<br>Please find attached the appointment letter from KBL Services Ltd.<br><br><b>Documents Required:</b><br>
            Marks Sheet: SSLC and PUC, Degree also convocation certificates.<br>
            Address Proof: Aadhar and Voter ID, if present address is different, then supporting proof like rental agreement is required.<br>
            ID Proof: DL and PAN Card<br>
            Work Experience letter.<br><br>Note: All the above documents should be separately uploaded in the link as PDFs.<br>
            Background Verification is a mandatory activity for all joiners. If the BGV is positive, meaning all the records, address proofs and criminal verification being done for you should come as all clear.
            This is mandatory to have continued employment in KBL Services Limited.<br><br>
            <b>Please ensure fill your BackGround Verification Form immediately using the link below.</b><br>
            https://erp.teamproit.com/bg-entry-form 
            <br><br>
            <br> Regards, <br>  HR Department, <br>KBL Services Ltd,Bengaluru""".format(doc.applicant_name),
           
        attachments=[frappe.attach_print("Job Offer",doc.name,file_name="AppointmentletterForm", print_format="Appointment letter Form")]
    )

@frappe.whitelist()
def job_offer_email_list(name,applicant_email,applicant_name,job_applicant,branch_mail,reports_to,first_cc,second_cc,third_cc,designation_name):
    if applicant_email:
        if designation_name == 'CASA Marketing Associate':
            frappe.errprint("Attcahments")
            frappe.sendmail(
                # delayed=1,
                # recipients = 'jothi.m@groupteampro.com',
                recipients=applicant_email,
                cc=['evasengupta@kblservices.in','hrops@kblservices.in',branch_mail],
                subject="Post Joining Documents",
                message="""<p>Dear Sir/Madam,</p>
                    <p>Kindly find the attached documents for your reference and fill the details present in the format by taking print to complete the joining formalities.
                    </p><br> Do not revert to this mail, for any queries/updates pls drop a mail to hrops@kblservices.in<br> <br>Regards, <br>  HR Department, <br>KBL Services Ltd, Bengaluru""",
                now=True,
                attachments=[frappe.attach_print("Job Offer", name,
                    file_name="Joining Report", print_format="Joining Report"),frappe.attach_print("Job Offer", name,
                    file_name="Reporting Form", print_format="Reporting Form"),frappe.attach_print("Job Offer", name,
                    file_name="Checklist", print_format="Checklist"),frappe.attach_print("Job Offer", name,
                    file_name="Form 11", print_format="Form 11"),frappe.attach_print("Job Offer", name,
                    file_name="PF Form", print_format="PF Form"),frappe.attach_print("Job Offer", name,
                    file_name="Undertaking Form", print_format="Undertaking Form"),frappe.attach_print("Job Offer", name,
                    file_name="Employee Joining Kit", print_format="Employee Joining Kit"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Code of Conduct",print_format="Code of Conduct"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Code of Conduct Acknowledgement",print_format="Code of Conduct Acknowledgement"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Attendance Register",print_format="Attendance Register"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="ID Card Request",print_format="ID Card Request"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Gratuity Policy",print_format="Gratuity Policy"),frappe.attach_print("Job Offer", name,
                    file_name="PF Opt Out Declaration",print_format="PF Opt Out Declaration")]
            )
        else:
            frappe.errprint("Attcahments")
            frappe.sendmail(
                # delayed=1,
                # recipients = 'jothi.m@groupteampro.com',
                recipients=applicant_email,
                cc=['evasengupta@kblservices.in','hrops@kblservices.in',branch_mail],
                subject="Post Joining Documents",
                message="""<p>Dear Sir/Madam,</p>
                    <p>Kindly find the attached documents for your reference and fill the details present in the format by taking print to complete the joining formalities.
                    </p><br>Do not revert to this mail, for any queries/updates pls drop a mail to hrops@kblservices.in<br><br> Regards, <br>  HR Department, <br>KBL Services Ltd, Bengaluru""",
                now=True,
                attachments=[frappe.attach_print("Job Offer", name,
                    file_name="Joining Report", print_format="Joining Report"),frappe.attach_print("Job Offer", name,
                    file_name="Reporting Form", print_format="Reporting Form"),frappe.attach_print("Job Offer", name,
                    file_name="Checklist", print_format="Checklist"),frappe.attach_print("Job Offer", name,
                    file_name="Form 11", print_format="Form 11"),frappe.attach_print("Job Offer", name,
                    file_name="PF Form", print_format="PF Form"),frappe.attach_print("Job Offer", name,
                    file_name="Undertaking Form", print_format="Undertaking Form"),frappe.attach_print("Job Offer", name,
                    file_name="Employee Joining Kit", print_format="Employee Joining Kit"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Code of Conduct",print_format="Code of Conduct"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Code of Conduct Acknowledgement",print_format="Code of Conduct Acknowledgement"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Attendance Register",print_format="Attendance Register"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="ID Card Request",print_format="ID Card Request"),frappe.attach_print("Job Applicant", job_applicant,
                    file_name="Gratuity Policy",print_format="Gratuity Policy")]
            )
    
     



def leave_restriction_lwp_before(doc, method):
    if doc.leave_type=='Leave Without Pay':
        from_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.from_date, str) else doc.from_date
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
        previous_date = frappe.utils.add_days(from_date, -1)    
        while True:
            day_of_week = previous_date.weekday()
            week_number = (previous_date.day - 1) // 7 + 1     
            is_holiday = frappe.db.exists('Holiday', {
                'parent': holiday_list,
                'holiday_date': previous_date.strftime('%Y-%m-%d')
            })       
            if not is_holiday and not (day_of_week == 5 and (week_number == 2 or week_number == 4)):
                break      
            previous_date = frappe.utils.add_days(previous_date, -1)       
        existing_leave_from = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name': ('!=', doc.name),
            'from_date': previous_date.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })
        
        existing_leave_to = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name': ('!=', doc.name),
            'to_date': previous_date.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })
        
        if existing_leave_from or existing_leave_to:
            frappe.throw('Another leave application found before the holiday')

@frappe.whitelist()
def leave_restriction_lwp_after(doc, method):
    if doc.leave_type=='Leave Without Pay':
        to_date = datetime.strptime(doc.from_date, '%Y-%m-%d') if isinstance(doc.to_date, str) else doc.to_date
        holiday_list = frappe.db.get_value('Employee', doc.employee, 'holiday_list')    
        next_day = frappe.utils.add_days(to_date, 1)
        while True:
            day_of_week = next_day.weekday()
            week_number = (next_day.day - 1) // 7 + 1        
            is_holiday = frappe.db.exists('Holiday', {'parent': holiday_list, 'holiday_date': next_day.strftime('%Y-%m-%d')})
            if not is_holiday and not (day_of_week == 5 and (week_number == 2 or week_number == 4)):
                break
            next_day = frappe.utils.add_days(next_day, 1)
        existing_leave_from = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name':('!=', doc.name),
            'from_date': next_day.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })
        existing_leave_to = frappe.db.exists('Leave Application', {
            'employee': doc.employee,
            'name':('!=', doc.name),
            'to_date': next_day.strftime('%Y-%m-%d'),
            'leave_type': doc.leave_type,
            'docstatus': ('!=', 2)
        })   
        if existing_leave_from or existing_leave_to:
            frappe.throw('Another leave application found after the holiday')

@frappe.whitelist()
def attachments_applicant(doc,method):
    name=doc.name
    applicant=doc.job_applicant
    frappe.errprint("Attachments")
    applicant=frappe.get_doc("Job Applicant",applicant)
    doc=frappe.get_doc("Job Offer",name)
    doc.pan_card=applicant.pan
    doc.driving_license=applicant.driving_license_
    doc.photo_attachment=applicant.image
    doc.signature=applicant.upload_your_signature
    doc.permanent_address_proof=applicant.permanent
    doc.present_address_proof=applicant.present_proof
    doc.sslc_marksheet=applicant.sslc_mark_sheets
    doc.marksheet=applicant.puc_
    doc.graduation_marksheet=applicant.graduation_
    doc.pg_marksheet=applicant.p_g_
    doc.previous_appointment_letter=applicant.appointment_letter
    doc.relieving_letter=applicant.reliving_letter
    doc.aadhar_=applicant.aadhar_id
    doc.save()
frappe.whitelist()
def create_leave_allocations():
    employees = frappe.db.sql("""
        SELECT employee_number, employee_name,date_of_joining
        FROM `tabEmployee`
        WHERE
            date_of_joining BETWEEN %(start_date)s AND %(end_date)s
            AND status = 'Active'
    """, {
        'start_date': '2024-06-01',
        'end_date': '2024-06-24'
    }, as_dict=True)
    for employee in employees:
        current_date=current_date = date.today()
        # current_date = datetime.now().date()
        
        # print(current_date_now)
        joining_year = employee.date_of_joining.year + 1
        to_date = current_date.replace(year=joining_year)
        if not frappe.db.exists("Leave Allocation", {"employee": employee.employee_number, "leave_type": "Privilege Leave"}):
            print(current_date)
            la_privilege = frappe.new_doc("Leave Allocation")
            la_privilege.employee = employee.employee_number
            la_privilege.leave_type = "Privilege Leave"
            la_privilege.new_leaves_allocated = 1.5
            la_privilege.from_date = current_date
            la_privilege.to_date = to_date
            la_privilege.carry_forward = 1
            la_privilege.save(ignore_permissions=True)
            la_privilege.submit()

        if not frappe.db.exists("Leave Allocation", {"employee": employee.employee_number, "leave_type": "Sick Leave"}):
            la_sick = frappe.new_doc("Leave Allocation")
            la_sick.employee = employee.employee_number
            la_sick.leave_type = "Sick Leave"
            la_sick.new_leaves_allocated = 1
            la_sick.from_date = current_date
            la_sick.to_date = to_date
            la_sick.save(ignore_permissions=True)
            la_sick.submit()
# @frappe.whitelist()
# def submit_att():
#     from_date='2024-07-01'
#     to_date='2024-07-31'
# 	att = frappe.db.sql("""select * from `tabAttendance` where attendance_date between '%s' and '%s' """%(from_date,to_date),as_dict=1)
#     for i in att:
# 	    frappe.db.sql("""update `tabAttendance` set workflow_='G' where name="HR-ATT-2024-30851" """,as_dict = True)



# @frappe.whitelist()
# def outward_register_number(employee):
#     frappe.errprint(employee)
#     job_applicant = frappe.db.get_value('Employee', {'name': employee}, 'job_applicant')
#     frappe.errprint(job_applicant)

#     outward_register_number = frappe.db.get_value('Job Offer', {'job_applicant': job_applicant}, 'outward_register_number')
#     if outward_register_number:
#         frappe.errprint(outward_register_number)
#     else:
#         outward_register_number = frappe.db.get_value('Job Offer', {'job_applicant': job_applicant}, 'name')
#         frappe.errprint(outward_register_number)
#         # return job_offer_name
    
#     return outward_register_number


@frappe.whitelist()
def offer_correction():
    checkin = frappe.db.sql("""update `tabJob Offer` set workflow_state='Draft' where name="KSL/P-2024-00176" """,as_dict = True)



@frappe.whitelist()
def contract_renewal_alert_notify():
    start_date = nowdate()
    end_date = add_days(nowdate(),30)
    exp_employees = frappe.db.sql("""
        SELECT name, employee_name, designation, contract_end_date
        FROM `tabEmployee` 
        WHERE contract_end_date BETWEEN %s AND %s
        AND status = 'Active'
    """, (start_date, end_date), as_dict=True)
    for emp in exp_employees: 
        approvers = []
        hod = frappe.db.get_value("Employee", {"name": emp.name}, ["reports_to"])
        hod_mail = frappe.db.get_value("Employee", {"name": hod}, ["user_id"]) if hod else None
        emp_mail = frappe.db.get_value("Employee", {"name": emp.name}, ["user_id"])
        hod_name = frappe.db.get_value("Employee", {"name": hod}, ["employee_name"]) 
        lm1 = frappe.db.get_value("Employee", {"name": emp.name}, ["line_manager_1"]) 
        lm2 = frappe.db.get_value("Employee", {"name": emp.name}, ["line_manager_2"]) 
        line_manager_1 = frappe.db.get_value('Employee',{'name':lm1},'user_id') if lm1 else None
        line_manager_2 = frappe.db.get_value('Employee',{'name':lm2},'user_id') if lm2 else None
        if line_manager_1:
            approvers.append(line_manager_1)
        if hod_mail:
            approvers.append(hod_mail)
        if line_manager_2:
            approvers.append(line_manager_2)
        print (hod)
        frappe.sendmail(
                recipients=emp_mail,
                # cc=hod_mail if hod_mail else [], 
                cc = approvers, 
                subject='Contract Ending Reminder',
                message="""
                    <b>Dear {}</b><br><br>
                    <p>With reference to your contractual term ending at KBL Services Ltd as {}, 
                    we would like to inform you that your contract will be ending as on {}
                    <br>
                    <br>
                    We would be pleased to hear your willingness to continue your services with us. Otherwise, kindly do write to us to hrops@kblservices.in regarding the same so that we can proceed with further formalities.
                    </p>
                    Thanks & Regards,<br>
                    HR Department,<br>
                    KBL Services Ltd, Bengaluru<br>
                    *This email has been automatically generated. Please do not reply*
                """.format(emp.employee_name,emp.designation,emp.contract_end_date)
            )

@frappe.whitelist()
def mail_alert_for_contract_renewal_alert_notify():
    job = frappe.db.exists('Scheduled Job Type', 'contract_renewal_alert_notify')
    
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")
        sjt.update({
            "method": 'kbl.custom.contract_renewal_alert_notify',  
            "frequency": 'Cron',  
            "cron_format": '* 09 * * *'  
        })
        sjt.save(ignore_permissions=True)
