// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Promoter Sales Capture', {
	brand: function(frm) {

		frappe.db.get_list('Item', {
			filters: {
				"brand": frm.doc.brand
			},
			fields: ['item_name'],
			limit: 500,
		}).then(res => {
			var arr=[]
			res.forEach(function (item, index) {
				arr.push([item["item_name"]])
			  });
			  set_field_options("item_name", arr)
		});

		
	}
});
