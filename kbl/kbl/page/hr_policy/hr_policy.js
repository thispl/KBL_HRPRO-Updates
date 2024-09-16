frappe.pages['hr-policy'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'HR Policy',
		single_column: true
	});
	frappe.breadcrumbs.add("HR");

	$(frappe.render_template("hr_policy")).appendTo(page.body.addClass("no-border"));
}