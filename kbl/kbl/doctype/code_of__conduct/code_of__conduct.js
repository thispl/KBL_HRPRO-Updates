frappe.ui.form.on('Code of  Conduct', {
    refresh: function(frm) {
        console.log("HI")
        if (frm.doc.code_of_conduct) {
            console.log("HI")
            var html_view = '<iframe src="' + frm.doc.code_of_conduct + '" width="800" height="600"></iframe>';
            $(frm.fields_dict['view'].wrapper).html(html_view);
        }
    },
    code_of_conduct: function(frm) {
        console.log("HI")
        if (frm.doc.code_of_conduct) {
            console.log("HI")
            var html_view = '<iframe src="' + frm.doc.code_of_conduct + '" width="800" height="600"></iframe>';
            $(frm.fields_dict['view'].wrapper).html(html_view);
        }
    },
    onload: function(frm) {
        console.log("HI")
        if (frm.doc.code_of_conduct) {
            console.log("HI")
            var html_view = '<iframe src="' + frm.doc.code_of_conduct + '" width="800" height="600"></iframe>';
            $(frm.fields_dict['view'].wrapper).html(html_view);
        }
    },
});