// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Planogram', {
	refresh: function(frm) {
		frappe.call({
			doc : frm.doc,
			method : 'fetch_html',
			freeze : true,
			freeze_message : 'Getting All Items'
		}).then((res) => {
			frm.set_df_property('shelf_preview', 'options',res.message)
			refresh_field('shelf_preview');
		})
	 }
});

frappe.ui.form.on('Planogram Items',{
	row:function(frm,cdt,cdn){
		var d=locals[cdt][cdn];
		var max_rows=parseInt(cur_frm.fields_dict["max_rows"]["value"])
		if (d.row==0){
			frappe.throw("Can't Set row to 0")
		}
		if (d.row>max_rows){
			frappe.throw("You are setting row above the limit of Max Rows")
		}
		
	}
});