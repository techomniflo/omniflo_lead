import frappe
import json

#gives stores data with status and address of it.
@frappe.whitelist()
def stores_list_data():
    stores_list = frappe.db.sql("""select c.customer_name as 'Customer Name', max(vi.creation) as 'Latest Visit log',vi.status, concat(a.address_line1," ",a.address_line2) as address,a.city,a.state,a.country,a.pincode from `tabVisit Log` as vi join `tabCustomer` as c on vi.customer=c.name join `tabAddress` as a on a.name=customer_primary_address where customer is not null and customer!="" group by customer;""",as_dict=True)
    return stores_list