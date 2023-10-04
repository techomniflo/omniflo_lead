import frappe

@frappe.whitelist(allow_guest=True)
def get_customer():
	data=frappe.db.sql("""select c.name from `tabCustomer` as c where c.customer_status in ('Live','Pseudo Live') and c.name not in ( select si.customer from `tabSales Invoice` as si where si.company="Omniway Technologies Pvt Ltd" and si.customer=c.name) order by c.name;""",as_list=True)
	return data