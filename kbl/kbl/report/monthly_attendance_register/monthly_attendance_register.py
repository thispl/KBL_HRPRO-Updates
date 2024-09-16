# Copyright (c) 2013, TEAMPRO and contributors
# For license information, please see license.txt

from frappe.utils import getdate, date_diff, comma_and, formatdate, get_datetime, flt, get_last_day, cstr
from datetime import datetime, timedelta
from frappe import msgprint, _
from erpnext.hr.utils import get_holiday_list_for_employee
from erpnext.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates, get_end_date
import frappe


day_abbr = [
	"Mon",
	"Tue",
	"Wed",
	"Thu",
	"Fri",
	"Sat",
	"Sun"
]

month_abbr = {
	"Jan": '01',
	"Feb": '02',
	"Mar": '03',
	"Apr": '04',
	"May": '05',
	"Jun": '06',
	"Jul": '07',
	"Aug": '08',
	"Sep": '09',
	"Oct": '10',
	"Nov": '11',
	"Dec": '12'
}

status_map = {
	"Present": "P",
	"Absent": "A",
	" ": "A",
	"Workflow" : "NA",
	"Rejected":"REJ",
	"Late" : "L",
	"Leave Without Pay": "LOP",
	"Casual Leave": "CL",
	"Sick Leave": "SL",
	"Privilege Leave": "PL",
	"Maternity Leave":'ML',
	"Compensatory Off": "CO",
	"Compensatory Leave": "CO",
	"Weekly Off": "WO",
	"Week Off": "WO",
	"Half Day": "HD",
	"Holiday": "HH",
	"NJ":"NJ"
}

def execute(filters=None):
	columns, data = [], []
	row = []
	year = filters.year
	employee_details = get_employee_data(filters, year)
	filtered_month = month_abbr[filters.month]
	start_date = f"{year}-{filtered_month}-01"
	from_date = datetime.strptime(start_date, "%Y-%m-%d")
	to_date = get_last_day(from_date)
	total_days_in_month = to_date - from_date.date()

	columns = get_columns(filters, total_days_in_month.days, from_date)

	for emp in employee_details:
		row = [emp.name, emp.employee_name, emp.designation]

		for i in range(total_days_in_month.days + 1):
			day = from_date + timedelta(days=i)
			status = get_attendance_data(emp.name, day)
			if status:
				row.append(status_map.get(status))
			else:
				holiday_type = check_holiday(day, emp.name)
				if holiday_type:
					status = holiday_type
					row.append(status_map.get(status))
				else:
					row.append(status_map.get(status,"A"))
			
		data.append(row)
	return columns, data

def get_attendance_data(employee, attendance_date):
	status = ""
	late_entry = frappe.get_value('Attendance', {'employee': employee, 'attendance_date': attendance_date}, 'late_entry')
	status = frappe.get_value('Attendance', {'employee': employee, 'attendance_date': attendance_date}, 'status')
	workflow_state=frappe.get_value('Attendance', {'employee': employee, 'attendance_date': attendance_date}, 'workflow_state')
	if workflow_state != "Approved by HR" or workflow_state != "Approved":
		if late_entry == 1 and status == "Present":
			status = "Late"
		elif status=='Present' and late_entry == 0:
			status=='Present'
		else:
			holiday_type = check_holiday(attendance_date, employee)
			if holiday_type and status != "On Leave":
				status = holiday_type
			elif holiday_type and status == "On Leave":
				status = frappe.get_value('Attendance', {'employee': employee, 'attendance_date': attendance_date}, 'leave_type')
			elif status == "On Leave" and not holiday_type:
				status = frappe.get_value('Attendance', {'employee': employee, 'attendance_date': attendance_date}, 'leave_type')
					
	elif workflow_state == "Pending for Sales Manager":
		status = "Workflow"
	elif workflow_state == "Rejected":
		status = "Rejected"
	else:
		if status=='':
			holiday_type = check_holiday(attendance_date, employee)
			if holiday_type:
				status = holiday_type
		elif status=='Absent':
			holiday_type = check_holiday(attendance_date, employee)
			if holiday_type:
				status = holiday_type 
	return status

def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off, `tabHoliday`.description from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	desc = ''
	if holiday :
		# if doj <= holiday[0].holiday_date:
		if holiday[0].weekly_off == 1:
			status = "Weekly Off"
		else:
			status = "Holiday"
		# else:
		# 	status = 'NJ'
	return status
		

def get_columns(filters, total_days_in_month, from_date):
	columns = []
	columns += [
		_("Employee ID") + ":Employee:150",
		_("Employee Name") + ":Data/:200",
		_("Designation") + ":Data/:200"
	]
	days = []
	for i in range(total_days_in_month + 1):
		day = from_date + timedelta(days=i)
		day_name = day_abbr[getdate(day).weekday()]
		days.append(cstr(day.day) + " " + day_name + "::65")
	columns += days

	return columns

def get_employee_data(filters, year):
	dates = get_start_end_dates('Monthly', filters.month)
	conditions = ''
	latest_date_of_leaving = []
	employee_details = frappe.db.sql("""
	SELECT name, employee_name, designation, department, branch, company, holiday_list FROM `tabEmployee` WHERE status = 'Active' UNION ALL
	SELECT name, employee_name, designation, department, branch, company, holiday_list FROM `tabEmployee`WHERE status = 'Inactive'""", as_dict=True)
	latest_date_of_leaving = frappe.db.sql("""
		SELECT name, employee_name, designation, department, branch, company, last_working_day
		FROM `tabEmployee`
		WHERE status = 'Left'  AND (relieving_date >= '{start_date}' OR date_of_termination >= '{start_date}') {conditions}
	""".format(start_date=dates.start_date, conditions=conditions), as_dict=True)
	employee_details.extend(latest_date_of_leaving)
	return employee_details
