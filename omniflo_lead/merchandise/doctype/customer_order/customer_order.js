// Copyright (c) 2023, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Order', {
	refresh: function(frm) {
		frm.fields_dict['item_group'].get_query = function(doc) {
			return {
				filters: {
					"name": ['in',['Food & Grocery','Purplle','Personal Care']]
				}
			}
		}
		$("input[data-target='Item Group']").prop('placeholder', 'All');
		frm.fields_dict['warehouse'].get_query = function(doc) {
			return {
				filters: {
					"name": ['in',['Kormangala WareHouse - OS']]
				}
			}
		}

	},
	get_items(frm){
		cur_frm.clear_table("items");
		cur_frm.refresh_field('items');
		frappe.call({
			doc : frm.doc,
			method : 'fetch_items',
			freeze : true,
			freeze_message : 'Getting All Items'
		}).then((res) => {
				refresh_field('items');
		})
	}
});
