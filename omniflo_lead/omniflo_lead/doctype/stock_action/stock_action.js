// Copyright (c) 2023, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Action', {
	// refresh: function(frm) {

	// }
});
function set_item(frm,cdt,cdn) {
	let item = locals[cdt][cdn];
	if (item.item_code){
		console.log("hello")
		frappe.call({
			args:{
				item_code:item.item_code,
				uom:item.uom,
				qty:item.qty
			},
			method : 'erpnext.stock.doctype.stock_entry.stock_entry.get_uom_details',
			freeze : true,
			freeze_message : 'converting'
		}).then((res)  => {
			item.transfer_qty=res.message['transfer_qty']
			item.conversion_factor=res.message['conversion_factor']
			refresh_field('items');
		})
	}
}

frappe.ui.form.on('Stock Action Item',{
	uom(frm, cdt, cdn){
		set_item(frm,cdt,cdn)
	},
	qty(frm, cdt, cdn){
		set_item(frm,cdt,cdn)
	}
});