
var index=0;       //global variable

//on load page in frappe page
frappe.pages['image-viewer'].on_page_load = function(wrapper) {

     	frappe.call({
     		method:"omniflo_lead.omniflo_lead.page.image_viewer.image_viewer.get_details",
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
			title: 'Image-Viewer',
			single_column: true
		});
		console.log(data)
		console.log(index)
		let $btn = page.add_inner_button('Back', () => Back(wrapper,data));
		let $btn4 = page.add_inner_button('Next',() => Next(wrapper,data));
		

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

let Back = function(wrapper,data){
	index = index-1
	callback_return(wrapper,data)

}

// This function is used to show next image and hide reason_div
let callback_return =function (wrapper,data){
	console.log(index,"in callback function")


	if (data.length==0 || data.length <= index){
		page.body.empty()
		$("<br><h5>There is no image in Queue to be reviewed</h5>").appendTo(page.body)
	}
	else if (index<0) {
		page.body.empty()
		// $("<br><h5>There is no image in to be reviewed</h5>").appendTo(page.body)
		index=-1
	}
	else
		{
		console.log("when index in range of data")
		var customer = data[index]['customer']
		var image = data[index]['image']
		var picture_type = data[index]['picture_type']
		var date_and_time = data[index]['date_and_time']
		var full_name = data[index]['full_name']
		if (index==0){
			console.log("if index is 0")
			$(frappe.render_template("image_viewer", 
				{customer:customer,image:image,picture_type:picture_type,date_and_time:date_and_time,full_name:full_name})).appendTo(page.body);


		}
		else{
			console.log("after index 0")
			page.body.empty()
			console.log("The image link is",data[0]['image'])
			$(frappe.render_template("image_viewer", 
				{customer:customer,image:image,picture_type:picture_type,date_and_time:date_and_time,full_name:full_name})).appendTo(page.body);
		}
	}
}

