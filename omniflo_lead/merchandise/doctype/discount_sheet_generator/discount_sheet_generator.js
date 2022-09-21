// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Discount Sheet Generator', {
	// refresh: function(frm) {

	// }
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
			})
		});
	}

});
