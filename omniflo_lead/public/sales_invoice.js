frappe.ui.form.on('Sales Invoice', {

    customer: function(frm){
        frappe.db.get_doc('Customer',frm.doc.customer).then((values)=>{
            if (values.customer_status!='Live' && values.customer_status!='On-boarded'){
                frappe.throw("Customer is not Live or not On-boarded its "+values.customer_status+"\n Agent Name"+values.manager_name)
            }
            else{
                frappe.msgprint("Customer is of Agent Name"+values.manager_name)
            }
        })
    },
    validate: function(frm){
        frappe.db.get_doc('Customer',frm.doc.customer).then((values)=>{
            if (values.customer_status!='Live' && values.customer_status!='On-boarded'){
                frappe.throw("Customer is not Live or not On-boarded its "+values.customer_status)
            }
        })
    }

});
