frappe.ready(function() {
	// bind events here
	// getLocation()
	function getLocation() {
		if (navigator.geolocation) {
		 navigator.geolocation.getCurrentPosition(showPosition);
		}
	}

	function showPosition(position) {
		console.log(position.coords.longitude)
		console.log(position.coords.latitude)
		frappe.web_form.set_value('latitude', position.coords.latitude);
		frappe.web_form.set_value('longitude', position.coords.longitude);
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
	function get_live_promoter(){
		frappe.call({
			method:"omniflo_lead.merchandise.web_form.promoter_logs.promoter_logs.live_promoter",
			freeze:true,
			callback: function(r){
				var res=r.message
				console.log(res)
				frappe.web_form.set_df_property('promoter', 'options', res)
			}
		});
	}

	function on_save_event(){
		if (frappe.web_form.doc.is_present==1){
			frappe.web_form.set_value("leave_type","")
			frappe.web_form.set_value("leave_duration","")
			frappe.web_form.set_value("reason","")
		}
		var validate=frappe.web_form.validate_section()
		var validate_geo=false
			if ((frappe.web_form.doc.latitude && frappe.web_form.doc.longitude)|| (frappe.web_form.doc.is_present==0) ){
				validate_geo=true
				
			}
			else{
				frappe.msgprint({
					title: "Message",
				  message: "<ul><li>latitude</li> <li> longitude </li><ul>",
				  indicator: "orange"
				  })
			}
			if (validate==true && validate_geo==true) {
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
		frappe.web_form.set_value('is_present',1)

		get_live_promoter()
		get_live_customer()
		getLocation()
	}


})