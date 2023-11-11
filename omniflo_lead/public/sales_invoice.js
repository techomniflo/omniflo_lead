frappe.ui.form.on('Sales Invoice', {

    refresh:function(frm){
        if (frm.doc.docstatus==0 && frm.doc.is_return==0){
                frm.add_custom_button(__('Remove Stock Out Qty'), function(){
                
                    frappe.call({
                    doc:frm.doc,
                    method: 'remove_stock_out_qty',
                    freeze:true,
                    freeze_message:"processing",
                    async: false,
                    callback: function(r) {

                        if (!r.exc) {
                            const array = r.message
                            var count=0
                            array.forEach(function (item, index) {
                                frm.get_field("items").grid.grid_rows[item-1-count].remove()
                                count=count+1
                            })
                            frm.refresh_field('items')
                        }
                    
                    }
                }); 

        });
    }


    if (frm.doc.is_return==1 && frm.doc.docstatus==0){
        mark_return_button(frm)
    }
},

    customer: function(frm){
        if (frm.doc.customer==""){
            return 
        }
        frappe.db.get_doc('Customer',frm.doc.customer).then((values)=>{
            if (values.customer_status!='Live' && values.customer_status!='On-boarded' && frm.doc.is_return==0){
                frappe.msgprint({message:"Customer is not Live or not On-boarded its "+values.customer_status+" Agent Name  "+values.manager_name,indicator:"red",title:"Error"})
                frm.set_value("customer", "")
            }
            else{
                frappe.msgprint("Customer is of Agent Name"+values.manager_name)
            }
            
        })
    },
    validate: function(frm){
        frappe.db.get_doc('Customer',frm.doc.customer).then((values)=>{
            if (values.customer_status!='Live' && values.customer_status!='On-boarded' && frm.doc.is_return==0){
                frappe.throw("Customer is not Live or not On-boarded its "+values.customer_status)
            }
        })
    },
    is_return:function(frm){
        if (frm.doc.is_return==1 && frm.doc.docstatus==0){
        mark_return_button(frm)
        }
        else{
            frm.remove_custom_button('Mark Return')
        }
    }
});

function mark_return_button(frm){
    frm.add_custom_button(__('Mark Return'), function(){
        const dialog= new frappe.ui.Dialog({
            title: __("Update Items"),
            fields: [
                {
                    fieldname:"item_code",
                    fieldtype:"Link",
                    label:"Item Code",
                    options: 'Item',
                    onchange: function(e) {
                        if(this.value){
                            dialog.set_value("uom","Piece")
                        }
                    }
                },
                {
                    fieldtype:'Float',
                    fieldname:"qty",
                    default: 0,
                    read_only: 0,
                    in_list_view: 1,
                    label: __('Qty')
                },
                {
                    fieldtype:'Link',
                    options:"UOM",
                    fieldname:"uom",
                    label:"UOM",
                },
                {
                    fieldtype:'Section Break'
                },
                {
                    fieldtype:'Button',
                    fieldname:'bulk_return',
                    label:'Bulk Return'
                }

            ],
            primary_action: function(values) {
             frappe.call({
                doc:frm.doc,
                method: 'fifo_qty',
                freeze:true,
                freeze_message:"processing",
                async: false,
                args: {'item':values},
                callback: function(r) {
                        dialog.clear()
                            if (r.message){
                                frappe.msgprint({
                                    title: __('Warning'),
                                    indicator: 'red',
                                    message: __(r.message)
                                });
                            }
                        frm.get_field('items').grid.add_new_row()
                        frm.get_field('items').grid.grid_rows[frm.doc.items.length-1].remove()
                }
                })

                refresh_field("items");
            },
            primary_action_label: __('Update'),
            secondary_action:function(values){
                dialog.hide();
            },
            secondary_action_label: __('Close')
        }).show();

        dialog.fields_dict.bulk_return.input.onclick = function(){
            dialog.hide()
           new frappe.ui.FileUploader({
                as_dataurl: !0,
                allow_multiple: !1,
                restrictions: {
                  allowed_file_types: [".csv"]
                },
                on_success(n) {
                  var r = frappe.utils.csv_to_array(frappe.utils.get_decoded_string(n.dataurl)),
                    o = r[2];
                    
                    frm.clear_table('items')
                    frm.refresh_field('items')
                    frappe.call({
                        doc:frm.doc,
                        method: 'bulk_return',
                        freeze:true,
                        freeze_message:"processing",
                        async: false,
                        args: {'arr':r},
                        callback: function(r) {
                              frm.refresh_field('items')
                        }
                        })
                    
                }
              })
        }
    });
    
}

