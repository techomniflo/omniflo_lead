
var index=0;       //global variable

//on load page in frappe page
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
		let $btn4 = page.add_inner_button('Next',() => Next(wrapper,data));
		let $btn = page.add_inner_button('Approve', () => approve(wrapper,data));
		let $btn2 = page.add_inner_button('Hold', () => on_hold(wrapper,data));
		let $btn3 = page.add_inner_button('Reject', () => get_reason(wrapper,data));

		
		$btn3.css({"background-color":"Red","color":"white"});
		$btn.css({"background-color":"Green","color":"white"});
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

// Approve function write status Approve in 'Audit Log Details'
let approve = function(wrapper,data){
	var approved_brand=""
	get_checked=$("#Brand-Div :checkbox:checked")
	for (let i = 0; i < get_checked.length; i++) {
		if (i!=get_checked.length-1){
		approved_brand += get_checked[i].value+","
	}
	else{
		approved_brand += get_checked[i].value
	}
		}
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

// This function shows reason div and add buttion submit
let get_reason = function(wrapper,data){
	$('#reason_div').show()
	$('#Brand-Div').hide()

	page.add_inner_button('Submit',() => on_click_submit(wrapper,data))
	
}

// This function get reason from get reason and pass to reject function and call reject function 
var on_click_submit = function (wrapper,data){
	reason=""
	counter=false
	var type_of_reason=['Poor_Store','People_in_frame','Blurry_Photo','Improper_Angle',"Shelf_Not_in_Focus","Other_products_on_the_Shelf",'Poor_Placement',"Hygiene_Issues","Object_Cutoff","Irrelevant_Photo","Wrong_Orientation","Improper_Lighting"]	
	type_of_reason.forEach(function(item,count) {
		if ($('#'+item).is(":checked")){
			if (counter){
				reason=reason+","+$('#'+item).val()
				}
			else{
				reason=$('#'+item).val()
				counter=true
			}
		}
	});
	if ($("#other").val()!=""){
		reason=reason+" ,"+$("#other").val();
	}
	
	console.log(reason)
	reject(wrapper,data,reason)

}

// This function write status = Reject and reason = 'reason from function on_click_submit' on `tabAudit Log Details`
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
     			
     			page.remove_inner_button('Submit')
     			
     		}
     	});
}

// This function is used to show next image and hide reason_div
let callback_return =function (wrapper,data){
	console.log(index,"in callback function")


	if (data.length==0 || data.length <= index){
		page.body.empty()
		$("<br><h5>There is no image in Queue to be reviewed</h5>").appendTo(page.body)
	}
	else
		{
		console.log("when index in range of data")
		var customer = data[index]['customer']
		var image = data[index]['image']
		var picture_type = data[index]['picture_type']
		var date_and_time = data[index]['date_and_time']
		var full_name = data[index]['full_name']
		var brand1=data[index]['brand1']
		var brand2=data[index]['brand2']
		if (index==0){
			console.log("if index is 0")
			$(frappe.render_template("image_approver", 
				{customer:customer,image:image,picture_type:picture_type,date_and_time:date_and_time,full_name:full_name,brand1:brand1,brand2:brand2})).appendTo(page.body);
				$("#reason_div").hide();
				show_brand(brand1,brand2,picture_type)
				page.remove_inner_button('Submit')

		}
		else{
			console.log("after index 0")
			page.body.empty()
			console.log("The image link is",data[0]['image'])
			$(frappe.render_template("image_approver", 
				{customer:customer,image:image,picture_type:picture_type,date_and_time:date_and_time,full_name:full_name,brand1:brand1,brand2:brand2})).appendTo(page.body);
			$("#reason_div").hide();
			show_brand(brand1,brand2,picture_type)
			page.remove_inner_button('Submit')

		}
	}
}

let show_brand = function(brand1,brand2,picture_type){
	for (let i = 0; i < brand1.length; i++) {
		var input="<label><input type='checkbox'  value='"+brand1[i][0]+"' id='"+brand1[i][0]+"' >"+brand1[i][0]+"</label></br>"
		$('#section1').append(input)
		if (picture_type=='Shelf' && brand1[i][1]==1){
			$("#section1 :input:last").prop('checked',true)
		}
		
		} 
	for (let i = 0; i < brand2.length; i++) {
		var input="<label><input type='checkbox'  value='"+brand2[i][0]+"' id='"+brand2[i][0]+"' >"+brand2[i][0]+"</label></br>"
		$('#section2').append(input)
		if (picture_type=='Shelf' && brand2[i][1]==1){
			$("#section2 :input:last").prop('checked',true)
		}
		}
}
