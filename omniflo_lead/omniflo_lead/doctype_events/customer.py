import frappe
def validate(doc, event):
    if not doc.customer_id and doc.customer_group!='Brand Platform':
        max_cust_no=frappe.db.sql(""" select max(substring(c.customer_id,9,4)) from `tabCustomer` as c where c.customer_id is not null and c.customer_id!='' """)
        max_cust_no=int(max_cust_no[0][0])+1
        doc.customer_id="OMNI-01-"+str(max_cust_no)