frappe.pages['code-of-conduct'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Code of Conduct'),
		single_column: true
	});
	frappe.breadcrumbs.add("HR");

	$(frappe.render_template("code_of_conduct")).appendTo(page.body.addClass("no-border"));
}