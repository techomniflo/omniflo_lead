import frappe
import json

#gives stores data with status and address of it.
@frappe.whitelist()
def stores_list_data():
    stores_list = frappe.db.sql("""select c.customer_name as 'Customer Name', max(vi.creation) as 'Latest Visit log',vi.status, concat(a.address_line1," ",a.address_line2) as address,a.city,a.state,a.country,a.pincode from `tabVisit Log` as vi left join `tabCustomer` as c on vi.customer=c.name left join `tabAddress` as a on a.name=customer_primary_address where customer is not null and customer!="" and c.customer_group!="Brand Platform" group by customer;""",as_dict=True)
    return stores_list

@frappe.whitelist()
def stores_data_with_status():
    store_list=frappe.db.sql("""select `tabCustomer`.customer_name,AL.status,(concat (A.address_line1," ",A.address_line2)) as address,A.city,A.state,A.pincode,`tabCustomer`.longitude,`tabCustomer`.latitude from `tabVisit Log` as AL left join `tabCustomer` on `tabCustomer`.name=AL.customer left join `tabDynamic Link` as dl on dl.link_name=`tabCustomer`.name left join `tabAddress` as A on A.name=dl.parent  where AL.modified in (select max(modified) from `tabVisit Log` where AL.customer=customer) and `tabCustomer`.customer_name is not null group by `tabCustomer`.customer_name;""",as_dict=True)
    return store_list