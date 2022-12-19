frappe.ready(function() {
	var brand_details;

	function setting_value_item_code(){

		var item_name=frappe.web_form.get_value('item_name').split(",")
		frappe.web_form.set_df_property('item_name','options',item_name[0])
		frappe.web_form.set_value("item_name",item_name[0])
		if (item_name[2]){
			frappe.web_form.set_value("item_code",item_name[2])
		}
		console.log(item_name)
		console.log(item_name[2])

	}

	function setting_value_item_name(){
		
		brand=frappe.web_form.get_value("brand")
		frappe.web_form.set_df_property('item_name','options',brand_details[brand])

	}
	function setting_brand(){
		frappe.call({
			method:"omniflo_lead.merchandise.web_form.promoter_sales_capture.promoter_sales_capture.fetch_billed_details",
			freeze:true,
			args:{
				customer:frappe.web_form.get_value("customer")
			},
			callback: function(r){
				var res=r.message
				console.log(res)
				brand_details=res
				frappe.web_form.set_df_property('brand', 'options', Object.keys(brand_details))
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
		$("[data-fieldname='gender']").find('label').append(' / ಗ್ರಾಹಕ ಲಿಂಗ')
		$("[data-fieldname='age']").find('label').append(' / ಗ್ರಾಹಕ ವಯಸ್ಸು')
		get_live_customer()
		$("[data-fieldname='item_name']").find('select').click(function(){
			frappe.web_form.set_df_property('item_name','options',brand_details[frappe.web_form.get_value('brand')])
		})
		frappe.web_form.on('brand', setting_value_item_name )
		frappe.web_form.on('customer',setting_brand)
		frappe.web_form.on('item_name',setting_value_item_code)
		
	}
})