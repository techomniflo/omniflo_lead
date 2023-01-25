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

frappe.ui.form.on('Customer Order Item', {
	item_code(frm, cdt, cdn){
		let item = locals[cdt][cdn];
		frappe.call({
			args:{
				brand:item.brand,
				customer:cur_frm.doc.customer
			},
			method : 'omniflo_lead.merchandise.doctype.customer_order.customer_order.is_brand_in_planogram',
			freeze : true,
			freeze_message : 'Getting All Items'
		}).then((res)  => {
			if (res.message==false){
				let msg_dialog = frappe.msgprint({
					title: __('Warning'),
					message: __('The Brand is not in Planogram <br> Are you sure you want to continue? <br>  <img src="https://s3.amazonaws.com/engine-omniflo/pictures/2023/01/25/Spotlight%20Issue/69M9NZFV_Bhai-kya-kar-raha-hai-tu-1024x711.webp" alt="Bhai ye kar raha h tu?" width="300" height="300">'),
					primary_action: {
						action: () => {
							msg_dialog.hide();
						},
						label: () => __("Continue"),
					},
					wide: true

				})
			}
			refresh_field('items');
		})
	}
});
