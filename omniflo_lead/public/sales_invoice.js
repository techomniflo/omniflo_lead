frappe.ui.form.on('Sales Invoice', {

    refresh:function(frm){
        if (frm.doc.docstatus==0){
        
                frm.add_custom_button(__('Remove Stock Out Qty'), function(){
                
                    frappe.call({
                    doc:frm.doc,
                    method: 'remove_stock_out_qty',
                    freeze:true,
                    async: false,
                    callback: function(r) {

                        if (!r.exc) {
                            frm.refresh_field('items')
                        }
                    
                    }
                });    

        });
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
    }

});
