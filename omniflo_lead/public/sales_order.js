frappe.ui.form.on('Sales Order', {
    setup:function(frm){
        frm.set_df_property('set_warehouse','read_only',1)
        frm.doc.set_warehouse="Kormangala WareHouse - OS"
        frm.doc.company="Omnipresent Services"

    },
    refresh: function(frm) {
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
                        // get qty from call
                        frappe.call({
                            method: 'omniflo_lead.omniflo_lead.api.planogram_api.get_suggested_items',
                            freeze:true,
                            async: false,
                            args: {
                                item_group:values.item_group || 'All',
                                customer:frm.doc.customer,
                                warehouse:frm.doc.set_warehouse
                            },
                            callback: function(r) {
                                if (!r.exc) {
                                    
                                    const array=r.message
                                    array.forEach(function (suggested_item, index) {
                                        
                                        item=frm.add_child('items',{'item_code':suggested_item['item_code'],'qty':suggested_item['qty']})
                                        if (frm.doc.delivery_date) {
                                            item.delivery_date = frm.doc.delivery_date;
                                            
                                        } else {
                                            frm.script_manager.copy_from_first_row("items", item, ["delivery_date"]);
                                        }
                                        frm.cscript.item_code(frm,'Sales Order Item',item.name)
                                      });
                                    
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