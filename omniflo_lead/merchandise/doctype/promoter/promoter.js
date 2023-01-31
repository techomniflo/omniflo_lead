// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Promoter', {
	refresh: function(frm) {
		cur_frm.fields_dict['item_group'].get_query = function(doc) {
			return {
				filters: {
					"name": ['in',['Food & Grocery','Purplle','Personal Care']]
				}
			}
		}

	}
});
