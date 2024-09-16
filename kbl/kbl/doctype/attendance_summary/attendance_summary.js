frappe.ui.form.on('Attendance Summary', {
	refresh(frm){
		frm.disable_save();
	},

	onload(frm){
		frm.set_value('from_date', frappe.datetime.month_start());
		frm.set_value('to_date', frappe.datetime.month_end());
		frm.set_value('employee_id', "");
		frm.set_value('employee_name', "");
		frm.trigger("fetch_emp_details");
		frm.trigger('get_data');
	},
	employee_id(frm){
		frm.trigger("fetch_emp_details");
		frm.trigger('get_data');
	},
	fetch_emp_details(frm){
		frappe.db.get_value("Employee", {'user_id': frappe.session.user}, ['employee','employee_name'], (r) => {
			if (r){
				frm.set_value('employee_id', r.employee);
				frm.set_value('employee_name', r.employee_name);
			}
		});
		frm.set_value('from_date', frappe.datetime.month_start());
		frm.set_value('to_date', frappe.datetime.month_end());
	},
	employee_id(frm){
		frm.trigger('get_data');
	},
	from_date(frm){
		frm.trigger('get_data');
	},
	to_date(frm){
		frm.trigger('get_data');
	},
	get_data(frm) {
		if (frappe.user.has_role("System Manager") && !frm.doc.employee_id) {
			frm.fields_dict.html.$wrapper.empty().append("<center><h2>Please select an employee</h2></center>");
			return;
		}
		if (frm.doc.employee_id && frm.doc.from_date && frm.doc.to_date) {
			// frappe.db.get_value('Employee', { "name": frm.doc.employee_id }, 'employee', (r) => {
				// if (r.employee) {
				frappe.call({
					method: "kbl.kbl.doctype.attendance_summary.attendance_summary.get_data",  // Updated module path
					args: {
						emp: frm.doc.employee_id,
						from_date: frm.doc.from_date,
						to_date: frm.doc.to_date
					},
					callback: function (r) {
						if (r.message) {
							frm.fields_dict.html.$wrapper.empty().append(r.message);
						}
						else {
							frm.fields_dict.html.$wrapper.empty().append("<center><h2>Attendance Not Found</h2></center>");
						}
					}
				});
		}
	},
});

window.createAttendance = function(employee, date) {
	frappe.call({
		method: "kbl.kbl.doctype.attendance_summary.attendance_summary.create_attendance_record",
		args: {
			employee: employee,
			attendance_date: date
		},
		freeze: true,
		freeze_message: __("Processing Attendance"),
		callback: function(r) {
			if(r.message) {
				frappe.msgprint(r.message);
				window.location.reload();
			}
		}
	});
};