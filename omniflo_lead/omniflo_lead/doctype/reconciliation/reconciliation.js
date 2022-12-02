// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Reconciliation', {
	refresh: function(frm) {

	},
	get_items_from_warehouse(frm){
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

frappe.ui.form.on('Reconciliation Items',{
	item_code(frm, cdt, cdn){
		let item = locals[cdt][cdn];
		frappe.call({
			args:{
				item_code:item.item_code,
				warehouse:cur_frm.doc.default_warehouse
			},
			method : 'omniflo_lead.omniflo_lead.doctype.reconciliation.reconciliation.get_current_qty',
			freeze : true,
			freeze_message : 'Getting All Items'
		}).then((res)  => {
			console.log(res.message)
			refresh_field('items');
		})
	}
});
