frappe.ui.form.on('Sales Order', {
    setup:function(frm){
        frm.set_df_property('set_warehouse','read_only',1)
        frm.doc.set_warehouse="Kormangala WareHouse - OS"
        frm.doc.company="Omnipresent Services"

    },
    refresh: function(frm) {
        cur_frm.fields_dict['items'].grid.wrapper.find('.row-index').css('height','auto')
		cur_frm.fields_dict['items'].grid.wrapper.find('.grid-static-col').css('height','auto')
		cur_frm.fields_dict['items'].grid.wrapper.find('.ellipsis').css('white-space','normal')
        frm.set_query('customer', () => {
            return {
                filters: {
                'customer_status': 'Live'
                }
            }
        })
        
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