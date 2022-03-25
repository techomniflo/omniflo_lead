// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Audit Log', {
	refresh: function(frm) {
		getLocation(frm);
	 },
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

function getLocation(frm) {
	if (navigator.geolocation) {
	 navigator.geolocation.getCurrentPosition(showPosition);
	
	}
}

function showPosition(position) {
	cur_frm.doc.latitude = position.coords.latitude;
	cur_frm.doc.longitude = position.coords.longitude;
  }