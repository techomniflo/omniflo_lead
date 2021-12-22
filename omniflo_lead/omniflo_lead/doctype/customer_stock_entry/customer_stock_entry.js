// Copyright (c) 2021, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Stock Entry', {
	// refresh: function(frm) {

	// }
	get_current_items(frm){
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
