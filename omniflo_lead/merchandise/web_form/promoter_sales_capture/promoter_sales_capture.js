frappe.ready(function() {
	
	frappe.web_form.set_df_property("qty", "read_only", 1)
	frappe.web_form.set_value("qty",1)
	frappe.web_form.on('brand', setting_value_item_name )
	function setting_value_item_name(){
		frappe.call({
			method:"omniflo_lead.merchandise.web_form.promoter_sales_capture.promoter_sales_capture.fetch_item",
			freeze:true,

			args:{
				brand:frappe.web_form.get_value("brand")
			},
			callback: function(r){
				var res=r.message
				var arr=[]
			res.forEach(function (item, index) {
				arr.push([item["item_name"]])
			  });
			  frappe.web_form.set_df_property('item_name', 'options', arr)
			}
		});
	}
	
})