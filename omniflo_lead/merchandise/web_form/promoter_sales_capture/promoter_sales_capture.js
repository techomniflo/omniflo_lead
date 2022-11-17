frappe.ready(function() {

	function setting_value_item_code(){
		frappe.call({
			method:"omniflo_lead.merchandise.web_form.promoter_sales_capture.promoter_sales_capture.fetch_item_code",
			freeze:true,
			args:{
				item_name:frappe.web_form.get_value("item_name"),
				brand:frappe.web_form.get_value("brand")
			},
			callback:function(r){
				frappe.web_form.set_value('item_code',r.message)
			}
		})
	}

	function setting_value_item_name(){
		frappe.call({
			method:"omniflo_lead.merchandise.web_form.promoter_sales_capture.promoter_sales_capture.fetch_item_name",
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

	function get_live_customer(){
		frappe.call({
			method:"omniflo_lead.merchandise.web_form.promoter_logs.promoter_logs.fetch_item",
			freeze:true,
			callback: function(r){
				var res=r.message
				console.log(res)
				frappe.web_form.set_df_property('customer', 'options', res)
			}
		});
	}
	function on_save_event(){
		var validate=frappe.web_form.validate_section()
			
			if (validate==true ) {
				frappe.web_form.save()
			frappe.web_form.page.empty()
			$("<h1>Your Response has been Submitted</h1>").appendTo(frappe.web_form.page)
			}
	}
	frappe.web_form.after_load = () => {
		$(".btn-primary").remove()
		frappe.web_form.add_button("Save","button",on_save_event)
		save_button=$('button:contains("Save")')
		save_button.css({"background-color":"Blue","color":"white"})

		get_live_customer()

		frappe.web_form.on('brand', setting_value_item_name )
		frappe.web_form.on('item_name',setting_value_item_code)
		
	}
})