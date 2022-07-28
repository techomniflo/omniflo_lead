frappe.ui.form.on('Customer', {

    account_manager: function(frm){
        frappe.db.get_value("User",frm.doc.account_manager,'full_name',(value)=>{
         frm.set_value('manager_name',value.full_name)
        })
    }

});
