// Copyright (c) 2023, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Action', {

	on_submit:function(frm){
		frappe.call({
			doc : frm.doc,
			method : 'set_previous_gle_queue',
			freeze : true,
			freeze_message : 'Getting All Items'
		}).then((res) => {
			
		})
	},
	refresh: function(frm) {

		from_warehouse_filters(frm)
		to_warehouse_fiters(frm)
		if(frm.doc.docstatus==0){
			frm.doc.stock_entry=""
			frm.doc.purchase_invoice=""
		}
		
		frm.fields_dict['purchase_receipt'].get_query = function(doc) {
			return {
				filters: {
					"docstatus":1
				}

				}
			}
		},
	reason_type: function(frm){
			to_warehouse_fiters(frm)
		}
});
function set_item(frm,cdt,cdn) {
	let item = locals[cdt][cdn];
	if (item.item_code){
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

function to_warehouse_fiters(frm){
	
	frm.fields_dict['to_warehouse'].get_query = function(doc) {
		
		if (frm.doc.reason_type=="Sampling" ||frm.doc.reason_type=="Dispose"){
			console.log(frm.doc.reason_type)
			return {
				filters: {
					"company": frm.doc.company,
					"warehouse_type":"Transit"
				}
			}
	
		}
		else{
			return {
				filters: {
					"company": frm.doc.company,
					"warehouse_type":frm.doc.reason_type
				}
			}
		}
	}
	
}

function from_warehouse_filters(frm){
	frm.fields_dict['from_warehouse'].get_query = function(doc) {
		return {
			filters: {
				"company": frm.doc.company,
				"warehouse_type":"Transit"
			}
		}

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