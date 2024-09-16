# Copyright (c) 2021, TEAMPRO and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff, format_datetime
from datetime import datetime, time, timedelta
from erpnext.hr.utils import get_holiday_list_for_employee

class AttendanceSummary(Document):
    pass

@frappe.whitelist()
def get_data(emp=None, from_date=None, to_date=None):
    # Check if employee is not selected
    if not emp:
        return "<center><h2>Please select an employee</h2></center>"

    # Calculate the number of days between from_date and to_date
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    # Generate a list of dates from from_date to to_date
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]

    # Get employee details from the database
    emp_details = frappe.db.get_value('Employee', emp, ['employee_name', 'department'])
    # Initialize the HTML table
    data = "<table class='table table-bordered=1'>"
    # Add a row with employee details
    data += "<tr><td style='border: 1px solid black;background-color:#ffedcc'><b>ID</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b style='color:purple'>%s</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b>Name</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b style='color:purple'>%s</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b>Dept</b></td><td style='border: 1px solid black;background-color:#ffedcc;' colspan=2><b style='color:purple'>%s</b></td></tr>" % (emp, emp_details[0], emp_details[1])
    # Add a row for date headers
    data += "<tr><td style='border: 1px solid black;background-color:#ffedcc'><b>Date</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b>Day</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b>Working</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b>In Time</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b>Out Time</b></td><td style='border: 1px solid black;background-color:#ffedcc;'><b>Status</b></td></tr>"
    
    # Loop through each date and fetch attendance data
    for date in dates:
        dt = datetime.strptime(date, '%Y-%m-%d')
        d = dt.strftime('%d-%b')
        day = dt.date().strftime('%a')
        status, working_hours, in_time, out_time = get_attendance_data(emp, date)
        data += "<tr><td style='border: 1px solid black;'>%s</td><td style='border: 1px solid black;'>%s</td><td style='border: 1px solid black;'>%s</td><td style='border: 1px solid black;'>%s</td><td style='border: 1px solid black;'>%s</td>" % (d, day, working_hours, in_time, out_time)
        
        # Check if the status is 'Absent'
        if status == 'Absent':
            # Add HTML for the 'Absent' status
            data += """<td style='border: 1px solid black;'>
                <table><tr>
                <td><b style='color:red'>%s</b></td>
                <td><form action='/app/leave-application/new-leave-application-1'>
                    <input type='submit' value='Leave' />
                </form></td>
                <td><button onclick="createAttendance('%s', '%s')">Present</button></td></tr></table>
                </td></tr>""" % (status, emp, date)
        else:
            # Add HTML for other statuses
            data += "<td style='border: 1px solid black;'><b style='color:green'>%s</b></td></tr>" % (status)
    
    # Close the HTML table
    data += "</table>"
    return data

def get_attendance_data(employee, attendance_date):
    status = 'Absent'
    working_hours = in_time = out_time = 0
    att = frappe.get_value('Attendance', {'employee': employee, 'attendance_date': attendance_date}, ['status', 'working_hours', 'in_time', 'out_time'])
    if att:  
        status = att[0]
        working_hours = att[1] or 0
        in_time = att[2] or 0
        out_time = att[3] or 0
        if status == "On Leave":
            status = frappe.get_value('Attendance', {'employee': employee, 'attendance_date': attendance_date}, 'leave_type')

    holiday_list = get_holiday_list_for_employee(employee)
    holiday_type = check_holiday(attendance_date, holiday_list)
    if holiday_type:
        status = holiday_type
    return status, working_hours, in_time, out_time

def check_holiday(date, holiday_list):
    holiday = frappe.db.sql("""SELECT `tabHoliday`.holiday_date, `tabHoliday`.weekly_off, `tabHoliday`.description 
        FROM `tabHoliday List` 
        LEFT JOIN `tabHoliday` ON `tabHoliday`.parent = `tabHoliday List`.name 
        WHERE `tabHoliday List`.name = '%s' AND holiday_date = '%s' """ % (holiday_list, date), as_dict=True)
    
    if holiday:
        if holiday[0].weekly_off == 1:
            return "Weekly Off"
        else:
            return "Holiday: " + holiday[0].description

@frappe.whitelist()
def create_attendance_record(employee, attendance_date):
	try:
		Late = 0
		from datetime import datetime, timedelta
		emp_id = frappe.db.get_value("Employee", {'status': 'Active', "employee_number": employee}, ['name'])
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
		attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d')
		formatted_date = attendance_date_obj.strftime('%d-%m-%Y')
		current_date = datetime.today().date()
		current_time = datetime.now().time()
		restriction=frappe.db.get_value("Employee", {'user_id': frappe.session.user}, ['no_restrictions'])
		if restriction == 0:
			if shift_type:
				if attendance_date_obj.date() == current_date and current_time > ltime_time:
					return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance cannot be marked one and half hour after the shift start timing.</p>'
				elif attendance_date_obj.date() < current_date:
					return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance cannot be marked for past dates</p>'
				elif attendance_date_obj.date() == current_date and etime_time <= current_time <= ltime_time:
					Late = 1
					if not frappe.db.exists("Attendance",{'employee': employee,'attendance_date': attendance_date}):
						attendance = frappe.new_doc('Attendance')
						attendance.employee = employee
						attendance.attendance_date = attendance_date
						attendance.late_entry = Late
						attendance.status = 'Present'
						attendance.docstatus = 0						
						attendance.insert()
						attendance.save()
						return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance marked one hour after shift start timing will be marked as Late.</p>'		
			else:
				if emp.designation != 'Data Entry Operator':
					if attendance_date_obj.date() == datetime.today().date():
						if time(10, 30) <= datetime.now().time() <= time(11, 59):
							Late = 1
							if not frappe.db.exists("Attendance",{'employee': employee,'attendance_date': attendance_date}):
								attendance = frappe.new_doc('Attendance')
								attendance.employee = employee
								attendance.attendance_date = attendance_date
								attendance.late_entry = Late
								attendance.status = 'Present'
								attendance.docstatus = 0						
								attendance.insert()
								attendance.save()
								return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance marked between 10.30AM and 11:59AM will be marked as Late.</p>'		
						elif datetime.now().time() > time(11, 59):
							return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance cannot be marked after 11:59AM.</p>'
					elif attendance_date_obj.date() < datetime.today().date():
						return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance cannot be marked for past dates</p>'
		if frappe.db.exists("Attendance",{'employee': employee,'attendance_date': attendance_date,'docstatus':('!=',2)}):
			return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance Already Present</p>'
		else:
			if not frappe.db.exists("Attendance",{'employee': employee,'attendance_date': attendance_date,'docstatus':('!=',2)}):
				attendance = frappe.new_doc('Attendance')
				attendance.employee = employee
				attendance.attendance_date = attendance_date
				attendance.late_entry = Late
				attendance.status = 'Present'
				attendance.docstatus = 0						
				attendance.insert()
				attendance.save()
				return '<p style="color: red; font-weight: bold; letter-spacing: 1px;">Attendance marked Successfully</p>'
		frappe.errprint('hello2')
		attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d')
		formatted_date = attendance_date_obj.strftime('%d-%m-%Y')
	except Exception as e:
		error_message = "Processing Attendance".format(str(e))
		return error_message
	


