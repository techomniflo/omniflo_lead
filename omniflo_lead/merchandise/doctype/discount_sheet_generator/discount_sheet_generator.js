// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Discount Sheet Generator', {
	refresh: function(frm) {
		if (frm.doc.docstatus==1){
			frm.set_df_property("credit_note", "hidden",0)
			if(frm.doc.credit_note==1){
				frm.set_df_property("credit_note", "read_only",1)
			}
		}
	},
	add: function(frm){
		const fields = [
			{fieldtype:"Link", label: __("Brand Offer"), fieldname:"brand_offer",options:"Brand Offers"}
		];
		frappe.prompt(fields, function(filters){
			frappe.call({
				doc : frm.doc,
				method : 'fetch_items',
				freeze : true,
				args:{
					brand_offer:filters.brand_offer
				},
				freeze_message : 'Getting All Items'
			}).then((res) => {
					refresh_field('items');	
					refresh_field('invoices')
			})
		});
	}

});
