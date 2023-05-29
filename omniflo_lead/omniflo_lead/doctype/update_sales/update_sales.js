// Copyright (c) 2023, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Update Sales', {
	update_sales: function(frm) {
		frappe.call({
			doc : frm.doc,
			method : 'update_sales_in_background',
			freeze : true,
			freeze_message : 'calculating sales'
		}).then((res) => {
			frappe.set_route('background_jobs')
		})
	}
});
