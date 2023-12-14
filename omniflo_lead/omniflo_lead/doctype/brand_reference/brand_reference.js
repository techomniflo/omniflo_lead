// Copyright (c) 2023, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Brand Reference', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on('Brand Reference Links', {
	customer: function(frm,cdt,cdn) {
		var item=locals[cdt][cdn]
		item.party=item.customer
		item.supplier=""

	},
	supplier: function(frm,cdt,cdn) {
		var item=locals[cdt][cdn]
		item.party=item.supplier
		item.customer=""
	}
});