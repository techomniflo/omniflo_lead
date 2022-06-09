import frappe

def on_submit(doc, event):
    for item in doc.items:
        customer_bin = frappe.db.get_value('Customer Bin', {'customer': doc.customer, 'item_code': item.item_code})
        if not customer_bin:
            customer_bin = frappe.new_doc('Customer Bin')
            customer_bin.customer = doc.customer
            customer_bin.item_code = item.item_code
            customer_bin.available_qty = item.stock_qty
            customer_bin.stock_uom = item.stock_uom
            customer_bin.save(ignore_permissions = True)
            continue
        else:
            customer_bin = frappe.get_doc('Customer Bin', customer_bin)
            customer_bin.available_qty += item.stock_qty
            customer_bin.stock_uom = item.stock_uom
            customer_bin.save(ignore_permissions = True)
def on_cancel(doc,event):
    frappe.msgprint("Hey i am in doctype event")
    for item in doc.items:
        customer_bin = frappe.db.get_value('Customer Bin', {'customer': doc.customer, 'item_code': item.item_code})
        if not customer_bin:
            pass
        else:
            customer_bin = frappe.get_doc('Customer Bin', customer_bin)
            customer_bin.available_qty -= item.stock_qty
            customer_bin.stock_uom = item.stock_uom
            customer_bin.save(ignore_permissions = True)