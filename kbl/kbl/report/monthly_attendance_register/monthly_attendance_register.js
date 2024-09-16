// Copyright (c) 2016, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Attendance Register"] = {
    "filters": [
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
            "default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 
                "Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
            "reqd": 1
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": "2019\n2020\n2021\n2022\n2023\n2024\n2025\n2026",
            "default":  frappe.datetime.str_to_obj(frappe.datetime.get_today()).getFullYear(),
                
            "reqd": 1
        },
    ],
       formatter: function(value, row, column, data, default_formatter) {
            value = default_formatter(value, row, column, data);
            const summarized_view = frappe.query_report.get_filter_value('summarized_view');
            const group_by = frappe.query_report.get_filter_value('group_by');
    
            if (!summarized_view) {
                if ((group_by && column.colIndex > 3) || (!group_by && column.colIndex > 2)) {
                    if (value == 'A' )
                        value = "<span style='color:red'>" + value + "</span>";
                    else if (value == 'LOP' ||value == 'CL' || value == 'SL' || value == 'PL' || value == 'CO' || value == 'ML')
                        value = "<b><span style='color:#318AD8'>" + value + "</span></b>";
                    else if (value == 'L')
                        value = "<b><span style='color:#800080	'>" + "P" + "</span></b>";
                    else if (value == 'NA')
                        value = "<b><span style='color:#a13006	'>" + "NA" + "</span></b>";
                    else if (value == 'REJ')
                        value = "<b><span style='color:red'>" + "REJ" + "</span></b>";
                }
            }
    
            return value;
        }
    
};
