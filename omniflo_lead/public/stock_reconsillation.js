frappe.ui.form.on('Stock Reconciliation', {

    onload_post_render: function(frm) {

        //here we are removing button after onload event happen
        frm.remove_custom_button("Fetch Items from Warehouse")
        // $(".ellipsis[data-label='Fetch%20Items%20from%20Warehouse']").hide();

    }
});