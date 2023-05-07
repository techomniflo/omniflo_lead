// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Audit Log', {
	refresh: function(frm) {
		text_wrap_table(frm,'items')
		
		frm.fields_dict['item_group'].get_query = function(doc) {
			return {
				filters: {
					"name": ['in',[' Food & Grocery',' Personal Care',' Purplle']]
				}
			}
		}
		getLocation(frm);
		hide_add_row(frm);
	 },
	 validate(frm){
		return new Promise(function(resolve, reject){
			frappe.call({
				doc : frm.doc,
				method : 'fetch_difference_item',
				freeze : true,
				freeze_message : 'Getting All Items'
			}).then((res) => {
				if (res.message!="False"){
					frappe.confirm(
						res.message,
						function() {
							var negative = 'frappe.validated = false';
							resolve(negative);
						},
						function() {
							reject();
						}
					)
					
				}
				else{
					resolve();
				}
					
			})
		})
	 },
	get_current_items(frm){
		cur_frm.clear_table("items");
		cur_frm.refresh_field('items');
		frappe.call({
			doc : frm.doc,
			method : 'fetch_items',
			freeze : true,
			freeze_message : 'Getting All Items'
		}).then((res) => {
				refresh_field('items');
				text_wrap_table(frm,'items')
				hide_add_row(frm);

				
		})
	}
	
});
function text_wrap_table(frm,table){
	cur_frm.fields_dict[table].grid.wrapper.find('.row-index').css('height','auto')
	cur_frm.fields_dict[table].grid.wrapper.find('.grid-static-col').css('height','auto')
	cur_frm.fields_dict[table].grid.wrapper.find('.ellipsis').css('white-space','normal')
}

function getLocation(frm) {
	if (navigator.geolocation) {
	 navigator.geolocation.getCurrentPosition(showPosition);
	
	}
}

function showPosition(position) {
	cur_frm.doc.latitude = position.coords.latitude;
	cur_frm.doc.longitude = position.coords.longitude;
  }

function hide_add_row(frm) {
	cur_frm.fields_dict['items'].grid.wrapper.find('.grid-add-row').remove();
}
frappe.ui.form.on('Audit Log Items', {
	
	form_render(frm, cdt, cdn){
    	
        // frm.fields_dict.items.grid.wrapper.find('.grid-delete-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-duplicate-row').hide();
        // frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-append-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row-below').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row').hide();
    }
});