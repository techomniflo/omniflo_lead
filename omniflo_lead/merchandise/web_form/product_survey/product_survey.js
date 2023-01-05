frappe.ready(function() {
	
	function on_save_event(){
		var validate=frappe.web_form.validate_section()
			
			if (validate==true ) {
				frappe.web_form.save()
			frappe.web_form.page.empty()
			$("<h1>Your Response has been Submitted</h1>").appendTo(frappe.web_form.page)
			}
	}
	function get_checked_value(){
		get_checked=$("#reason_not_to_buy :checkbox:checked")
		var reason_not_to_buy=""
		for (let i = 0; i < get_checked.length; i++) {
			if (i!=get_checked.length-1){
			reason_not_to_buy += get_checked[i].value+","
		}
		else{
			reason_not_to_buy += get_checked[i].value
		}
			}
		
		var improve_the_product=""
		get_checked=$("#improve_the_product :checkbox:checked")
		for (let i = 0; i < get_checked.length; i++) {
			if (i!=get_checked.length-1){
				improve_the_product += get_checked[i].value+","
		}
		else{
			improve_the_product += get_checked[i].value
		}
			}
		frappe.web_form.set_value('improve_the_product',improve_the_product)
		frappe.web_form.set_value('reason_not_buy',reason_not_to_buy)

	}
	function add_check_box(){
		$("[data-fieldname='reason_not_buy']").find('input').hide()
		$("[data-fieldname='reason_not_buy']").find('div').find('.control-input').append("<div id='reason_not_to_buy'> </div>")
		const arr = ["It was too expensive", "Taste was not good", "Didnot trust the ingredients","Didnot know about the brand","Size was not preferred"]
		for (let i = 0; i < arr.length; i++){
			var input="<label><input type='checkbox'  value='"+arr[i]+"' id='"+arr[i]+"' >"+arr[i]+"</label></br>"
			$("[data-fieldname='reason_not_buy']").find('div').find('#reason_not_to_buy').append(input)
		}
		$("[data-fieldname='improve_the_product']").find('input').hide()
		$("[data-fieldname='improve_the_product']").find('div').find('.control-input').append("<div id='improve_the_product'> </div>")
		const arr1 = ["Lower the price", "Improve the taste", "Use better ingredients","Offer more sizes"]
		for (let i = 0; i < arr1.length; i++){
			var input="<label><input type='checkbox'  value='"+arr1[i]+"' id='"+arr1[i]+"' >"+arr1[i]+"</label></br>"
			$("[data-fieldname='improve_the_product']").find('div').find('#improve_the_product').append(input)
		}

	}
	function add_kannada(){
		$("[data-fieldname='customer_prefer']").find('label').append("<br> ಉತ್ಪನ್ನವನ್ನು ಆಯ್ಕೆ ಮಾಡುವ ಮೊದಲು ಗ್ರಾಹಕರು ಯಾವುದಕ್ಕೆ ಹೆಚ್ಚು ಆದ್ಯತೆ ನೀಡಿದರು?")
		$("[data-fieldname='price']").find('label').append("<br> ಉತ್ಪನ್ನದ ಬೆಲೆಯ ಬಗ್ಗೆ ಗ್ರಾಹಕರು ಹೇಗೆ ಭಾವಿಸಿದರು?")
		$("[data-fieldname='taste']").find('label').append("<br> ಉತ್ಪನ್ನದ ರುಚಿಯ ಬಗ್ಗೆ ಗ್ರಾಹಕರು ಹೇಗೆ ಭಾವಿಸಿದರು?")
		$("[data-fieldname='quality']").find('label').append("<br> ಉತ್ಪನ್ನದ ಗುಣಮಟ್ಟದ ಬಗ್ಗೆ ಗ್ರಾಹಕರು ಹೇಗೆ ಭಾವಿಸಿದರು?")
		$("[data-fieldname='reason_not_buy']").find('label').append("<br> ಗ್ರಾಹಕರು ಉತ್ಪನ್ನವನ್ನು ಏಕೆ ಖರೀದಿಸಲಿಲ್ಲ?")
		$("[data-fieldname='improve_the_product']").find('label').append("<br> ಉತ್ಪನ್ನವನ್ನು ಸುಧಾರಿಸಲು ಅಥವಾ ಅದನ್ನು ಹೆಚ್ಚು ಆಕರ್ಷಕವಾಗಿಸಲು ಬ್ರ್ಯಾಂಡ್ ಏನು ಮಾಡಬಹುದು?")
		$("[data-fieldname='specific_testimonials']").find('label').append("<br> ನೀವು ನೆನಪಿಸಿಕೊಳ್ಳಬಹುದಾದ ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಪ್ರಶಂಸಾಪತ್ರಗಳು ಇದೆಯೇ?")
		$("[data-fieldname='comment']").find('label').append("<br> ಯಾವುದೇ ಇತರ ಒಳನೋಟ ಅಥವಾ ಕಾಮೆಂಟ್ ಅನ್ನು ಯಾವುದಾದರೂ ಹಂಚಿಕೊಳ್ಳಿ.")
	}
	

	// bind events here
	frappe.web_form.after_load = () => {
		$(".btn-primary").remove()
		frappe.web_form.add_button("Save","button",on_save_event)
		save_button=$('button:contains("Save")')
		save_button.css({"background-color":"Blue","color":"white"})
		add_kannada()
		add_check_box()
		$("#reason_not_to_buy :checkbox").change(get_checked_value)
		$("#improve_the_product :checkbox").change(get_checked_value)

	}
})