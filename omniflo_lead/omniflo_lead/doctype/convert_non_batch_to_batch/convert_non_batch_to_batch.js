// Copyright (c) 2022, Omniflo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Convert non batch to batch', {
	refresh: function(frm) {

	},
	convert_non_batch_to_has_batch: function(frm){
		handle_convert_non_batch_to_has_batch(frm);
	}
});


var handle_convert_non_batch_to_has_batch = function(frm){
	frappe.warn('Are you sure you want to proceed?',
				'This is a low level procedure and may harm your data if misused!!',
				() => {
					// action to perform if Continue is selected
					frappe.prompt([
						{
							label: 'Item Group',
							fieldname: 'item_group',
							fieldtype: 'Link',
							options: 'Item Group'
						},
						{
							label: 'Batch Number Series',
							fieldname: 'batch_number_series',
							fieldtype: 'Data'
						}
					], (values) => {
						var group = values.item_group;
						var series = values.batch_number_series;
						frappe.call({
                            method: "omniflo_lead.omniflo_lead.doctype.convert_non_batch_to_batch.convert_non_batch_to_batch.get_items_without_has_batch_in_item_group",
                            args: {
                                group: group,
								series: series
                            },
                            callback: function(res){
                                if (res && res.message){
									frappe.confirm('Are you sure you want to proceed with ' + res.message +' items in '+ group + ' Group?',
    									() => {
        										// action to perform if Yes is selected
												frappe.call({
													method: "omniflo_lead.omniflo_lead.doctype.convert_non_batch_to_batch.convert_non_batch_to_batch.handle_convert_non_batch_to_has_batch",
													args: {
														group: group,
														series: series
													},
													callback: function(res){
														if (res && res.message){
															frappe.msgprint('Successfully processed '+ res.message +' Items.');
														}
													}
												});
    									}, () => {
        										// action to perform if No is selected
    									}
									)
								}
							}
						});
					})
				},
				'Continue',
					//true // Sets dialog as minimizable
				)
}
