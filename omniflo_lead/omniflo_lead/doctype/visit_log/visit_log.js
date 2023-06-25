// Copyright (c) 2021, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Visit Log', {
	refresh: function(frm) {
		if ((frm.doc.latitude==null || frm.doc.latitude==undefined) && (frm.doc.longitude==null || frm.doc.longitude==undefined)){
		getLocation(frm);
		}
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
