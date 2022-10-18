import frappe

def get_context(context):
	# do your magic here
	pass
@frappe.whitelist(allow_guest=True)
def fetch_item():
	data=frappe.db.sql("""select c.name from `tabCustomer` as c where c.customer_status='Live' and c.name not in ( select si.customer from `tabSales Invoice` as si where si.company="Omniway Technologies Pvt Ltd" and si.customer=c.name) order by c.name;""",as_list=True)
	return data
