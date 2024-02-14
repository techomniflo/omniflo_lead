import frappe

@frappe.whitelist(allow_guest=True)
def get_customer():
	data=frappe.db.sql("""select 
							* 
							from 
							(
								select 
								c.name as customer_id, 
								c.customer_name,
								c.customer_status
								from 
								`tabCustomer` as c 
								where 
								c.customer_status in ('Live', 'Pseudo Live') 
								and c.name not in (
									select 
									si.customer 
									from 
									`tabSales Invoice` as si 
									where 
									si.company = "Omniway Technologies Pvt Ltd" 
									and si.customer = c.name
								)
							) as customer 
							left join (
								select 
								dl.link_name, 
								a.address_line1, 
								a.address_line2, 
								a.state, 
								a.pincode 
								from 
								`tabDynamic Link` as dl 
								join `tabAddress` as a on a.name = dl.parent 
								where 
								dl.link_doctype = 'Customer' 
								and a.disabled = 0 
								and dl.parenttype = 'Address' 
								group by 
								dl.link_name
							) as address on customer.customer_id = address.link_name 
							order by 
							customer.customer_id
							""",as_dict=True)
	return data