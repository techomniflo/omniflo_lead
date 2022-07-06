import frappe
import json
import time
import datetime

#Gives total no live store of perticular brand -> int(number)
@frappe.whitelist()
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


#Gives name of brand with name of customer->brand1:customer1,customer2
@frappe.whitelist()
def stores_lives():
	values={"brand":frappe.request.args["brand"]}
	brand_with_store_name=frappe.db.sql("""select
	    it.brand,cb.customer
	from 
	    `tabCustomer Bin`  as cb
	    join  `tabItem`as it on cb.item_code = it.item_code
	where brand!="" and brand!="Test" and cb.customer!="" and cb.available_qty>0 and it.brand=%(brand)s
	group by brand,customer
	order by
	    it.brand,cb.customer""",values=values)
	di={}
	for i in brand_with_store_name:
		if i[0] not in di:
			di[i[0]]=[i[1]]
		else:
			di[i[0]].append(i[1])
	return di

#Gives total no of live inventory for perticular brand
@frappe.whitelist()
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

#Gives gmv(no. of item * mrp) amount of brand date wise 
@frappe.whitelist() 
def total_units_sold():
	values={"brand":frappe.request.args["brand"]}

	total_unit_sold_gmv=frappe.db.sql("""select 
	  posting_date, 
	  sum(total) as total_gmv
	from 
	  (
	    select 
	      si.`posting_date` as posting_date, 
	      sii.`item_code`, 
	      (
	        (i.`mrp`) * (sii.`qty`)
	      ) as total 
	    FROM 
	      `tabSales Invoice` as si
	      LEFT JOIN `tabSales Invoice Item` as sii
	      	 ON si.`name` = sii.`parent` 
	      LEFT JOIN `tabItem` as i
	       ON sii.`item_code` = i.`item_code` 
	    WHERE 
	      (
	        i.`brand` = %(brand)s 
	        AND (
	          si.`status` != 'Cancelled' 
	          and si.`status` != "Draft"
	          and si.`status` != "Return"
	          OR si.`status` IS NULL
	        ) 
	        OR si.`status` IS NULL
	      )
	  ) as nnnnnnn 
	where 
	  posting_date IN (
	    SELECT 
	      distinct(
	        `tabSales Invoice`.`posting_date`
	      ) 
	    from 
	      `tabSales Invoice` 
	    WHERE 
	      `tabSales Invoice`.`status` != 'Cancelled' 
	      and `tabSales Invoice`.`status` != "Draft"
	  )
	  group by posting_date

""",values=values,as_list=True)
	return total_unit_sold_gmv


#It gives you total no. of items billed from engine
@frappe.whitelist()
def unit_sold():
	values={"brand":frappe.request.args["brand"]}
	total_unit_sold=frappe.db.sql("""SELECT sum(`TabSales Invoice Item`.`qty`) AS `sum`
		FROM `tabSales Invoice`
		LEFT JOIN 
			`tabSales Invoice Item` `TabSales Invoice Item` ON `tabSales Invoice`.`name` = `TabSales Invoice Item`.`parent` LEFT JOIN `tabItem` `TabItem` ON `TabSales Invoice Item`.`item_code` = `TabItem`.`item_code`
		WHERE (`TabItem`.`brand` = %(brand)s
		AND (`tabSales Invoice`.`status` != 'Cancelled' and `tabSales Invoice`.`status`!="Draft"
			OR `tabSales Invoice`.`status` IS NULL)  OR `tabSales Invoice`.`status` IS NULL)""",values=values,as_list=True)
	
	total_inventory=frappe.db.sql("""select sum(available_qty) from (select
			it.brand,cb.customer,cb.item_code,cb.available_qty
		from 
			`tabCustomer Bin`  as cb
			join  `tabItem`as it on cb.item_code = it.item_code
		where brand!="" and brand!="Test" and cb.customer!="" and cb.available_qty>0 and it.brand=%(brand)s
		group by brand,customer,item_code
		order by
			it.brand,cb.customer) as total_available_qty""",values=values,as_list=True)

	di={'unit_billed_to_Store':total_unit_sold[0][0],'total_inventory_in_store':total_inventory[0][0],'unit_sold':total_unit_sold[0][0]-total_inventory[0][0]}
	return di

# It gives image with customer name
@frappe.whitelist()
def image_api():
	values={"brand":frappe.request.args["brand"]}
	image_with_customer_name=frappe.db.sql("""select distinct(ald.image),ald.status as status,al.customer,ald.creation as image_date from `tabAudit Log Details` as ald join `tabAudit Log` as al on al.name=ald.parent join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code where ali.current_available_qty > 0 and i.brand=%(brand)s and ald.image is not null order by ald.creation desc;""",values=values,as_dict=True)
	list_of_approve_image=[]
	for i in image_with_customer_name:
		if i['status']=="Approve":
			list_of_approve_image.append(i)
	return list_of_approve_image


# it gives time series gmv of audit log+sales invoice
@frappe.whitelist()
def time_series_gmv():
	values={"brand":frappe.request.args["brand"]}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,al.customer,ali.current_available_qty as qty,ali.item_name,i.mrp from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where i.brand=%(brand)s order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,si.customer,sii.qty,sii.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where i.brand=%(brand)s and si.`status` != 'Cancelled' and si.`status`!="Draft" order by si.posting_date;""",values=values,as_dict=True)

	#This function gives list of unique date
	def get_date(data):
		list_of_date=[]
		i=0
		while i<len(data):
			al_date=data[i]['date']
			if al_date in list_of_date:
				i+=1
				continue
			else:
				list_of_date.append(al_date)
				i+=1
		return list_of_date



	def crate_dict_for_give_date(date,x):
		customer_dict={}
		date_date=time.strptime(date,"%d-%m-%y")
		for i in range(len(x)):
			doctype_date=time.strptime(x[i]['date'],"%d-%m-%y")
			if date_date==doctype_date:
				customer=x[i]['customer']
				item_name=x[i]['item_name']
				qty=x[i]['qty']
				mrp=x[i]['mrp']
				if customer not in customer_dict:
					customer_dict[customer]={item_name:[qty,mrp]}
				else:
					if item_name not in customer_dict[customer]:
						customer_dict[customer][item_name]=[qty,mrp]
		print(customer_dict)
		return customer_dict

	def get_dictionary_with_date(data):
		di={}
		list_of_date=get_date(data)
		for i,date in enumerate(list_of_date):
			di[date]=crate_dict_for_give_date(date,data)
		return di
	audit_dictionary=get_dictionary_with_date(audit_data)
	sales_dictionary=get_dictionary_with_date(sales_data)


	#merging audit_dictionary and sales_dictionary
	for i in list(audit_dictionary.keys()):
		if i not in sales_dictionary:
			sales_dictionary[i]=audit_dictionary[i]
		else:
			customer_list=list(audit_dictionary[i].keys())
			for j in customer_list:
				if j not in sales_dictionary[i]:
					sales_dictionary[i][j]=audit_dictionary[i][j]
				else:
					item_list=list(audit_dictionary[i][j].keys())
					for k in item_list:
						if k not in sales_dictionary[i][j]:
							sales_dictionary[i][j][k]=audit_dictionary[i][j][k]
						else:
							sales_dictionary[i][j][k][0]=audit_dictionary[i][j][k][0]


	# below that we sort the sales_dictionary according to time
	data_keys=list(sales_dictionary.keys())
	timestamp_list=[]
	for i in data_keys:
		d=datetime.datetime.strptime(i,"%d-%m-%y")
		timestamp = datetime.datetime.timestamp(d)
		timestamp_list.append(timestamp)
	timestamp_list.sort()

	for j in range(len(timestamp_list)):
		convert = datetime.datetime.fromtimestamp(timestamp_list[j])
		timestamp_list[j]=convert.strftime("%d-%m-%y")
	print(timestamp_list)
	# new_dictionary contain sorted data according to time
	new_dictionary={}
	for j in timestamp_list:
		new_dictionary[j]=sales_dictionary[j]
	return new_dictionary