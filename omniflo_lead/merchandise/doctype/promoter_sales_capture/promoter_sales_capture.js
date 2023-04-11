// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Promoter Sales Capture', {
	brand: function(frm) {
		frm.fields_dict['item_code'].get_query = function(doc) {
			return {
				filters: {
					"brand": frm.doc.brand
				}
			}
		}

		
	}
});
