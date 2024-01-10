frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        text_wrap_items_table(frm)
      
        
        if (frm.doc.docstatus==0){
            // adding custom button Get Suggested Planogram Qty
          frm.add_custom_button(__('Get Suggested Planogram Qty'), function(){
                // defining a Dialog which is popup to take input for suggested qty
            let d = new frappe.ui.Dialog({
                title: 'Enter details',
                fields: [
                    {
                        label: 'Item Group',
                        fieldname: 'item_group',
                        fieldtype: 'Link',
                        options: "Item Group",
                        filters:{'name':["in",['Food & Grocery',"Purplle","Personal Care"]]}
                    }],
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        // add qty to child table items from add_planogram_qty function
                        frappe.call({
                            doc:frm.doc,
                            method: 'add_planogram_qty',
                            freeze:true,
                            async: false,
                            args: {
                                item_group:values.item_group || 'All',
                                customer:frm.doc.customer,
                                warehouse:frm.doc.set_warehouse
                            },
                            callback: function(r) {
                                if (!r.exc) {
                                    frm.refresh_field('items')
                                }
                                text_wrap_items_table(frm)
                                d.hide(); //hide dialog when all appeded all items
                            }
                        });
  
                        
                    }
                
                })
            d.show()  //show dialog 
        });

    }

  }

});

function text_wrap_table(frm,table){
	frm.fields_dict[table].grid.wrapper.find('.row-index').css('height','auto')
	frm.fields_dict[table].grid.wrapper.find('.grid-static-col').css('height','auto')
	frm.fields_dict[table].grid.wrapper.find('.ellipsis').css('white-space','normal')
}
function text_wrap_items_table(frm){
	frm.fields_dict['items'].grid.wrapper.find('.next-page').click(function(){text_wrap_table(frm,'items')})
	frm.fields_dict['items'].grid.wrapper.find('.prev-page').click(function(){text_wrap_table(frm,'items')})
	frm.fields_dict['items'].grid.wrapper.find('.first-page').click(function(){text_wrap_table(frm,'items')})
	frm.fields_dict['items'].grid.wrapper.find('.last-page').click(function(){text_wrap_table(frm,'items')})
	text_wrap_table(frm,'items')
}