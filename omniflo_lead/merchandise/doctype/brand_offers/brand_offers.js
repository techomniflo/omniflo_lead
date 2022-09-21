// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Brand Offers', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on('Brand Offers Items',{
	offer_price: function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		d.difference=d.mrp-d.offer_price
		d.offer_percentage=(d.difference/d.mrp)*100
		cur_frm.refresh_field("items");
	}


});
