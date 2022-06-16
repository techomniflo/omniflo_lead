// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Audit Log', {
	refresh: function(frm) {
		getLocation(frm);
		hide_add_row(frm);
	 },
	get_current_items(frm){
		frappe.call({
			doc : frm.doc,
			method : 'fetch_items',
			freeze : true,
			freeze_message : 'Getting All Items'
		}).then((res) => {
				refresh_field('items');
				hide_add_row(frm);

				
		})
	}
	
});

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
	cur_frm.fields_dict['items'].grid.wrapper.find('.grid-add-row').hide();
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