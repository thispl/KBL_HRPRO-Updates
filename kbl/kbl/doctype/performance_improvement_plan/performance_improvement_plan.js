// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Improvement Plan', {

	refresh: function(frm) {
		if(!frm.doc.__islocal){
			frm.add_custom_button(__("Print"), function () {
				var f_name = frm.doc.name
				var print_format = "PIP Letter";
				window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
					+ "doctype=" + encodeURIComponent("Performance Improvement Plan")
					+ "&name=" + encodeURIComponent(f_name)
					+ "&trigger_print=1"
					+ "&format=" + print_format
					+ "&no_letterhead=0"
				));
			})
		}
		
	},
	last_date_to_achieve_target(frm){
		frm.set_value("month",frm.doc.last_date_to_achieve_target)
	}
});
