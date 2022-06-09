import frappe
import json

@frappe.whitelist(allow_guest=True)
def total_live_store():
    values={"brand":frappe.request.args["brand"]}
    count_of_store = frappe.db.sql("""select count(customer) from (select
	    cb.customer
	from 
	    `tabCustomer Bin`  as cb
	    join  `tabItem`as it on cb.item_code = it.item_code
	where brand!="" and brand!="Test" and cb.customer!="" and cb.available_qty!=0 and it.brand=%(brand)s
	group by it.brand,cb.customer
	order by
	    it.brand,cb.customer) as total_customer
    """,values=values,as_list=True)
    return count_of_store

@frappe.whitelist(allow_guest=True)
def stores_lives():
	brand_with_store_name=frappe.db.sql("""select
	    it.brand,cb.customer
	from 
	    `tabCustomer Bin`  as cb
	    join  `tabItem`as it on cb.item_code = it.item_code
	where brand!="" and brand!="Test" and cb.customer!="" and cb.available_qty>0 
	group by brand,customer
	order by
	    it.brand,cb.customer""")
	di={}
	for i in brand_with_store_name:
		if i[0] not in di:
			di[i[0]]=[i[1]]
		else:
			di[i[0]].append(i[1])
	return di

@frappe.whitelist(allow_guest=True)
def total_inventory():
	values={"brand":frappe.request.args["brand"]}

	total_inventory=frappe.db.sql("""select sum(available_qty) from (select
	    it.brand,cb.customer,cb.item_code,cb.available_qty
	from 
	    `tabCustomer Bin`  as cb
	    join  `tabItem`as it on cb.item_code = it.item_code
	where brand!="" and brand!="Test" and cb.customer!="" and cb.available_qty>0 and it.brand=%(brand)s
	group by brand,customer,item_code
	order by
	    it.brand,cb.customer) as total_available_qty""",values=values,as_list=True)
	return total_inventory
    
@frappe.whitelist(allow_guest=True)
def unit_sold():
	values={"brand":frappe.request.args["brand"]}
	total_unit_sold=frappe.db.sql("""SELECT sum(`TabSales Invoice Item`.`qty`) AS `sum`
		FROM `tabSales Invoice`
		LEFT JOIN 
			`tabSales Invoice Item` `TabSales Invoice Item` ON `tabSales Invoice`.`name` = `TabSales Invoice Item`.`parent` LEFT JOIN `tabItem` `TabItem` ON `TabSales Invoice Item`.`item_code` = `TabItem`.`item_code`
		WHERE (`TabItem`.`brand` = %(brand)s
		AND (`tabSales Invoice`.`status` != 'Cancelled' and `tabSales Invoice`.`status`!="Draft"
			OR `tabSales Invoice`.`status` IS NULL)  OR `tabSales Invoice`.`status` IS NULL)""",values=values,as_list=True)
	return total_unit_sold