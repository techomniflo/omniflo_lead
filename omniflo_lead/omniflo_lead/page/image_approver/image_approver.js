var index=0;   //global variable

frappe.pages['image-approver'].on_page_load = function(wrapper) {

     	frappe.call({
     		method:"omniflo_lead.omniflo_lead.page.image_approver.image_approver.get_details",
     		freeze:true,
     		callback: function(r){
     			console.log(r.message)
     			data=r.message;
     			console.log(index)
     			new MyPage(wrapper,data);
     		}
     	});
     	
}

MyPage = Class.extend({
	init: function(wrapper,data) {
		page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Image-Approver',
			single_column: true
		});
		console.log(data)
		console.log(index)
		let $btn4 = page.add_inner_button('Pass',() => pass(wrapper,data));
		let $btn = page.add_inner_button('Approve', () => approve(wrapper,data));
		let $btn2 = page.add_inner_button('Hold', () => on_hold(wrapper,data));
		let $btn3 = page.add_inner_button('Reject', () => get_reason(wrapper,data,page));

		
		$btn3.css({"background-color":"Red","color":"white"});
		$btn.css({"background-color":"Green","color":"white"});
		callback_return(wrapper,data)
		
	},
	make: function(wrapper,data) {
        // 
	}
})

// this function trigger when pass button clicked
// Pass function do just like next image
let pass = function(wrapper,data){
	index = index+1
	callback_return(wrapper,data)

}


// Approve function write status Approve in 'Audit Log Details'
let approve = function(wrapper,data){
	frappe.call({
     		method:"omniflo_lead.omniflo_lead.page.image_approver.image_approver.approve",
     		freeze:true,
     		// freeze_message:_("hello gets call"),
     		args:{
     			data:data,
     			index:index
     		},
     		callback: function(r){
     			index=index+1
     			callback_return(wrapper,data)
     		}
     	});

	return 
}

// get_reason function get reason to reject from user
let get_reason = function(wrapper,data,page){

	var type_of_reason=['Blurry Photo','Improper Angle','Object Cutoff','Shelf Not in Focus','Hygiene Issues','Other products on the Shelf','Irrelevant Photo','Wrong Orientation']
	type_of_reason.forEach(function (item, count) {
		  page.add_inner_button(item,() => reject(wrapper,data,item),'Reason')
		});
	page.add_inner_button('Other',() => other(wrapper,data,page),'Reason')
	
}

// this is triggered when other in clicked in Reason
let other = function (wrapper,data,page){
	let field = page.add_field({
    label: 'Type reason',
    fieldtype: 'Data',
    fieldname: 'comment'
	});
	let $btn5 = page.add_inner_button('Submit', () => reject(wrapper,data,field.get_value()));
}

// This function write status Reject with reason given by user
let reject = function(wrapper,data,reason){
	frappe.call({
     		method:"omniflo_lead.omniflo_lead.page.image_approver.image_approver.reject",
     		freeze:true,

     		args:{
     			data:data,
     			index:index,
     			reason:reason
     		},
     		callback: function(r){
     			index=index+1
     			callback_return(wrapper,data)
     			var type_of_reason=['Blurry Photo','Improper Angle','Object Cutoff','Shelf Not in Focus','Hygiene Issues','Other products on the Shelf','Irrelevant Photo','Wrong Orientation','Other']
     			// page.remove_inner_button('Reason')
     			type_of_reason.forEach(function (item, count) {
					  page.remove_inner_button(item,'Reason')
					});
     			page.remove_inner_button('Submit')
     			page.clear_fields()
     			
     		}
     	});
}

// This function write Hold in status in 'Audit Log Details'
let on_hold = function(wrapper,data){
    frappe.call({
         method:"omniflo_lead.omniflo_lead.page.image_approver.image_approver.on_hold",
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
}


// This function is used to show next image and clear previous html
let callback_return =function (wrapper,data){
	console.log(index,"in callback function")

	if (data.length==0 || data.length <= index){
		// $("#myimg").attr("src","")
		page.body.empty()
		$("<br><h5>There is no image in Queue to be reviewed</h5>").appendTo(page.body)
	}
	else
		{
			console.log("i am in else function")
		var customer = data[index]['customer']
		var image = data[index]['image']
		var picture_type = data[index]['picture_type']
		var date_and_time = data[index]['date_and_time']
		var full_name = data[index]['full_name']
		if (index==0){
			console.log("in else if function")
			$(frappe.render_template("image_approver", 
				{customer:customer,image:image,picture_type:picture_type,date_and_time:date_and_time,full_name:full_name})).appendTo(page.body);
		}
		else{
			console.log("in else else function ")
			page.body.empty()
			console.log("hi have this data",data[0]['image'])
			$(frappe.render_template("image_approver", 
				{customer:customer,image:image,picture_type:picture_type,date_and_time:date_and_time,full_name:full_name})).appendTo(page.body);

		}
	}
}

