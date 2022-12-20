// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Reconciliation', {
	refresh: function(frm) {

	},
	add_brand: function(frm){
		const fields = [
			{fieldtype:"Link", label: __("Brand"), fieldname:"brand",options:"Brand"}
		];
		frappe.prompt(fields, function(filters){
			frappe.call({
				doc : frm.doc,
				method : 'fetch_brands_item',
				freeze : true,
				args:{
					brand:filters.brand
				},
				freeze_message : 'Getting All Items'
			}).then((res) => {
					refresh_field('items');
			})
		});
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
			item.current_quantity=res.message
			refresh_field('items');
		})
	}
});
