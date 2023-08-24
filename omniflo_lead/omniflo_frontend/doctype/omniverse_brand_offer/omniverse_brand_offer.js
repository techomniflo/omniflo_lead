// Copyright (c) 2023, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Omniverse Brand Offer', {
	setup: async function(frm) {
		const sub_brand_filters = await getFilters(frm);
		frm.set_query("sub_brand", {
			filters: [
				["brand", "in", sub_brand_filters]
			]
		});
		frm.set_query("brand",function(frm){
			return {
				filters:[
					['is_sub_brand','=',0]
				]
			}

		});
 
	},
	brand: async function(frm){
		const sub_brand_filters = await getFilters(frm);
		frm.set_query("sub_brand", {
			filters: [
				["brand", "in", sub_brand_filters]
			]
		});
	}
	
});


async function getFilters(frm) {
	const response = await frappe.db.get_list('Brand', {
		filters: {
			parent_brand: frm.doc.brand,
		},
		fields: ['brand']
	});

	var reFilters = [];
	if (response.length > 0) {
		for (let index = 0; index < response.length; index++) {
			reFilters.push(response[index]['brand']);
		}
	} else {
		reFilters.push(frm.doc.brand);
	}
	return reFilters;
}

