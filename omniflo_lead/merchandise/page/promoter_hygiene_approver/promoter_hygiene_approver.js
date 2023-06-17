
var index=0;       				//global variable
var selected_image_type="" 		//global variable

//on load page in frappe page
frappe.pages['promoter-hygiene-approver'].on_page_load = function(wrapper) {
	
     	frappe.call({
     		method:"omniflo_lead.merchandise.page.promoter_hygiene_approver.promoter_hygiene_approver.get_details",
     		freeze:true,
     		callback: function(r){
     			data=r.message;
     			new MyPage(wrapper,data);
     		}
     	});
     	
}

MyPage = Class.extend({
	init: function(wrapper,data) {
		page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Promoter Hygiene Approver',
			single_column: true
		});
		
		callback_return(wrapper,data)
		
		
	},
	make: function(wrapper,data) {
		

	}
})

// This shows next image
let Next = function(wrapper,data){
	index = index+1
	callback_return(wrapper,data)

}

// Approve function write status Approve in 'Promoter Hygiene Photos'
let approve = function(wrapper,data){
	frappe.call({
     		method:"omniflo_lead.merchandise.page.promoter_hygiene_approver.promoter_hygiene_approver.approve",
     		freeze:true,
     		args:{
     			data:data,
     			index:index,
     		},
     		callback: function(r){
     			index=index+1
     			callback_return(wrapper,data)
     			
     		}
     	});

	return 
}



// This function shows reason div and add buttion submit
let get_reason = function(wrapper,data){
	$('#reason_div').show()

	page.add_inner_button('Submit',() => on_click_submit(wrapper,data))
	
}

// This function get reason from get reason and pass to reject function and call reject function 
var on_click_submit = function (wrapper,data){
	reason=""
	var reject_reason = $('#reason_div input:checked')
	reject_reason.each(function (i, ob) { 

		if (reject_reason.length!=i+1){
			reason=reason+$(ob).val()+ ","
		}
		else{
			reason=reason+$(ob).val()	
		}
	})
	
	reject(wrapper,data,reason)

}

// This function write status = Reject and reason = 'reason from function on_click_submit' on `tabAudit Log Details`
let reject = function(wrapper,data,reason){
	remove_button()

	frappe.call({
     		method:"omniflo_lead.merchandise.page.promoter_hygiene_approver.promoter_hygiene_approver.reject",
     		freeze:true,

     		args:{
     			data:data,
     			index:index,
     			reason:reason
     		},
     		callback: function(r){
     			index=index+1
     			callback_return(wrapper,data)
     			page.remove_inner_button('Submit')
     			
     		}
     	});
	return
}

var on_change_event_in_select = function(){
	$("#select_image_type").change(function() {
        var type=$('#select_image_type').val();
		frappe.call({
			method:"omniflo_lead.merchandise.page.promoter_hygiene_approver.promoter_hygiene_approver.get_details",
			freeze:true,
			args:{
				type:type
			},
			callback: function(r){
				index=0
				selected_image_type=type
				remove_button()
				callback_return("",r.message)
			}
		});
    }); 
}

// This function will show button 
var show_button=function(wrapper,data){
	let $btn4 = page.add_inner_button('Next',() => Next(wrapper,data));
	let $btn = page.add_inner_button('Approve', () => approve(wrapper,data));
	let $btn3 = page.add_inner_button('Reject', () => get_reason(wrapper,data));

	$btn3.css({"background-color":"Red","color":"white"});
	$btn.css({"background-color":"Green","color":"white"});
	}

// This function will remove button
var remove_button=function(){
	page.remove_inner_button('Next')
	page.remove_inner_button('Approve')
	page.remove_inner_button('Reject')
}


// This function is used to show next image and hide reason_div
let callback_return =function (wrapper,data){

	show_button(wrapper,data)
	if (data.length==0 || data.length <= index){
		page.body.empty()
		$(frappe.render_template("end")).appendTo(page.body)
		on_change_event_in_select()
	}
	else
		{
		var customer = data[index]['customer']
		var image = data[index]['image']
		var picture_type = data[index]['type']
		var date_and_time = data[index]['creation']
		var promoter = data[index]['promoter']
		var item_group = data[index]['item_group']
		if (picture_type=='Selfie'){
			var hygiene_check_boxes = [['Check Uniform And ID Card',data[index]['check_uniform_and_id_card']]]
			}
		if (picture_type=='Asset'){
			var hygiene_check_boxes = [['Check In Category Placement',data[index]['check_in_category_placement']],
			['Set Merchandising',data[index]['set_merchandising']],
			['Set Offers',data[index]['set_offers']],
			['Clean Shelf and Product',data[index]['clean_products_and_shelf']]]
		}

	
		page.body.empty()
		$(frappe.render_template("promoter_hygiene_approver", 
			{customer:customer,image:image,picture_type:picture_type,date_and_time:date_and_time,promoter:promoter,item_group:item_group,hygiene_check_boxes:hygiene_check_boxes})).appendTo(page.body);
		$("#reason_div").hide();
		$('#select_image_type').val(selected_image_type) 
		on_change_event_in_select()
		page.remove_inner_button('Submit')

		
	}
}
