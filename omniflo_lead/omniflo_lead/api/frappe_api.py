import frappe
import json
import time
import datetime
import copy
from collections import defaultdict

#Gives total no live store of perticular brand -> int(number)
@frappe.whitelist()
def total_live_store():
    values={"brand":frappe.request.args["brand"]}
    count_of_store = frappe.db.sql("""select count(customer) from (select
	    cb.customer
	from 
	    `tabCustomer Bin`  as cb
	    join  `tabItem`as it on cb.item_code = it.item_code
	where brand!="" and brand!="Test" and cb.customer!="" and cb.available_qty>0 and it.brand=%(brand)s
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
	    it.brand,(select c.customer_name from `tabCustomer` as c where c.name=cb.customer)as customer
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


#It gives you total no. of unit sold to end customer (bill quantity-store-quantity)
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
	image_with_customer_name=frappe.db.sql("""select distinct(ald.image),ald.status as status,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ald.creation as image_date from `tabAudit Log Details` as ald join `tabAudit Log` as al on al.name=ald.parent join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code where ali.current_available_qty > 0 and i.brand=%(brand)s and ald.image is not null and ald.status='Approve' order by ald.creation desc;""",values=values,as_dict=True)
	return image_with_customer_name

@frappe.whitelist()
def time_series_gmv_data():
	values={"brand":frappe.request.args["brand"]}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,ali.item_name,i.mrp from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where i.brand=%(brand)s and al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where i.brand=%(brand)s  and si.`status` != 'Cancelled' and si.`status`!="Draft" and si.`status` != 'Return' order by si.posting_date;""",values=values,as_dict=True)

	return_data=frappe.db.sql("""select (select (DATE_FORMAT(SI.posting_date,'%%d-%%m-%%y')) as date from `tabSales Invoice` as SI where SI.name=si.return_against) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where i.brand=%(brand)s and si.`status` = 'Return' order by date;""",values=values,as_dict=True)

	#This function gives list of unique date
	def get_date(data):
		list_of_date=[]
		for i in data:
			list_of_date.append(i['date'])
		list_of_date=set(list_of_date)
		list_of_date=list(list_of_date)
		list_of_date.sort(key=lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
		return list_of_date



	def crate_dict_for_give_date(date,x,is_add):
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
					else:
						if is_add==True:
							customer_dict[customer][item_name][0]+=qty
		return customer_dict

	def get_dictionary_with_date(data,is_add):
		di={}
		list_of_date=get_date(data)
		for i,date in enumerate(list_of_date):
			di[date]=crate_dict_for_give_date(date,data,is_add)
		return di

	def merge_sales_and_return(sales_data,return_data):
		for date in list(return_data.keys()):
			if date in sales_data:
				for customer in list(return_data[date].keys()):
					if customer in sales_data[date]:
						for item in list(return_data[date][customer].keys()):
							if item in sales_data[date][customer]:
								difference=sales_data[date][customer][item][0]+return_data[date][customer][item][0]
								if difference <= 0:
									sales_data[date][customer].pop(item)
									if len(list(sales_data[date][customer].keys()))<=0:
										sales_data[date].pop(customer)
									if len(list(sales_data[date].keys()))<=0:
										sales_data.pop(date)
								else:
									sales_data[date][customer][item][0]=sales_data[date][customer][item][0]+return_data[date][customer][item][0]
		return sales_data
	audit_dictionary=get_dictionary_with_date(audit_data,is_add=False)
	sales_dictionary=merge_sales_and_return(get_dictionary_with_date(sales_data,is_add=True),get_dictionary_with_date(return_data,is_add=True))
	sales_invoice=copy.deepcopy(sales_dictionary)
	audit_invoice=copy.deepcopy(audit_dictionary)
	dates=list(sales_invoice.keys())+list(audit_invoice.keys())
	dates=list(set(dates))

	dates.sort(key=lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
	final_dictionary={}
	previous_data={}
	for i in dates:
		merged_customer={}
		sales_data=sales_invoice.get(i,{})
		audit_data=audit_invoice.get(i,{})
		sales_customer=list(sales_data.keys())
		audit_customer=list(audit_data.keys())
		for customer in sales_customer:
			if customer not in previous_data:
				previous_data[customer]=sales_data[customer]
				continue
			elif customer in previous_data:
				items=sales_data[customer]
				for item in items.keys():
					if item not in previous_data[customer]:
						previous_data[customer][item]=sales_data[customer][item]
					else:
						previous_data[customer][item][0]+=sales_data[customer][item][0]
		for customer in audit_customer:
			if customer not in previous_data:
				previous_data[customer]=audit_data[customer]
				continue
			if customer in sales_customer:
				pass
			if customer not in sales_customer:
				items=audit_data[customer]
				for item in items.keys():
					previous_data[customer][item]=audit_data[customer][item]
		both_customer=list(set(sales_customer+audit_customer))
		for customer in both_customer:
			merged_customer[customer]=copy.deepcopy(previous_data[customer])
		final_dictionary[i]=merged_customer
	return final_dictionary

@frappe.whitelist()
def gmv_sales_date_wise():
	values={"brand":frappe.request.args["brand"]}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,i.item_name,i.mrp from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where i.brand=%(brand)s and al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,i.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where i.brand=%(brand)s  and si.`status` != 'Cancelled' and si.`status`!="Draft" order by si.posting_date;""",values=values,as_dict=True)
	#This function gives list of unique date
	def get_date(data):
		list_of_date=[]
		for i in data:
			list_of_date.append(i['date'])
		list_of_date=set(list_of_date)
		list_of_date=list(list_of_date)
		list_of_date.sort(key=lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
		return list_of_date



	def crate_dict_for_give_date(date,x,is_add):
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
					else:
						if is_add==True:
							customer_dict[customer][item_name][0]+=qty
						if is_add==False:
							customer_dict[customer][item_name][0]=qty
		return customer_dict

	def get_dictionary_with_date(data,is_add):
		di={}
		list_of_date=get_date(data)
		for i,date in enumerate(list_of_date):
			di[date]=crate_dict_for_give_date(date,data,is_add)
		return di

	audit=get_dictionary_with_date(audit_data,is_add=False)
	sales=get_dictionary_with_date(sales_data,is_add=True)
	start_date=list(sales.keys())
	start=datetime.datetime.strptime(start_date[0],"%d-%m-%y")
	cumulative_sales={}
	cumulative_billed_with_date={}
	end=datetime.datetime.now()
	while start<=end:
		i=start.strftime("%d-%m-%y")
		if i in sales:
			customers=list(sales[i].keys())
			for customer in customers:
				if customer not in cumulative_sales:
					cumulative_sales[customer]=sales[i][customer]
				else:
					items=list(sales[i][customer].keys())

					for item in items:
						if item not in cumulative_sales[customer]:
							cumulative_sales[customer][item]=sales[i][customer][item]
						else:
							cumulative_sales[customer][item][0]+=sales[i][customer][item][0]
		start=start+datetime.timedelta(days=1)
		cumulative_billed_with_date[i]=copy.deepcopy(cumulative_sales)
	# pprint.pprint(cumulative_sales_with_date)
	cumulative_sales_with_date={}
	for i in audit.keys():
		if i in cumulative_billed_with_date:
			customers=audit[i].keys()
			for customer in customers:
				if customer in cumulative_billed_with_date[i]:
					items=audit[i][customer].keys()
					for item in items:
						if item in cumulative_billed_with_date[i][customer]:
							if i not in cumulative_sales_with_date:
								cumulative_sales_with_date[i]={customer:{item:audit[i][customer][item]}}
							if customer not in cumulative_sales_with_date[i]:
								cumulative_sales_with_date[i][customer]={item:audit[i][customer][item]}
							if item not in cumulative_sales_with_date[i][customer]:
								cumulative_sales_with_date[i][customer][item]=copy.deepcopy(audit[i][customer][item])
							cumulative_sales_with_date[i][customer][item][0]=cumulative_billed_with_date[i][customer][item][0] - audit[i][customer][item][0]
	sales_recorder={}
	count=0
	sales=[]
	for i in cumulative_sales_with_date.keys():
		customers=list(cumulative_sales_with_date[i].keys())
		for customer in customers:
			items=list(cumulative_sales_with_date[i][customer].keys())
			for item in items:
				if customer not in sales_recorder:
					sales_recorder[customer] = {item:copy.deepcopy(cumulative_sales_with_date[i][customer][item])}
					sales_recorder[customer][item][0]=0
				if item not in sales_recorder[customer]:
					sales_recorder[customer][item] = copy.deepcopy(cumulative_sales_with_date[i][customer][item])
					sales_recorder[customer][item][0]=0

				if (cumulative_sales_with_date[i][customer][item][0]-sales_recorder[customer][item][0]) != 0:
					diff=cumulative_sales_with_date[i][customer][item][0]-sales_recorder[customer][item][0]
					sales.append([i,customer,item,diff,cumulative_sales_with_date[i][customer][item][1]])

				count+=cumulative_sales_with_date[i][customer][item][0]-sales_recorder[customer][item][0]
				sales_recorder[customer][item] = copy.deepcopy(cumulative_sales_with_date[i][customer][item])
	sales_on_date={}
	for i in sales:
		if i[0] not in sales_on_date:
			sales_on_date[i[0]]={i[1]:{i[2]:[i[3],i[4]]}}
		if i[1] not in sales_on_date[i[0]]:
			sales_on_date[i[0]][i[1]]={i[2]:[i[3],i[4]]}
		if i[2] not in sales_on_date[i[0]][i[1]]:
			sales_on_date[i[0]][i[1]][i[2]]=[i[3],i[4]]
	return sales_on_date

@frappe.whitelist()
def warehouse_quantity():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("""select i.item_name,i.item_code,b.actual_qty as qty from `tabBin` as b join `tabItem` as i on i.item_code=b.item_code where b.warehouse="Kormangala WareHouse - OS" and i.brand=%(brand)s""",values=values,as_dict=True)

@frappe.whitelist()
def deployed_quantity():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("""select * from (select (select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer_name,i.item_name,sii.item_code,(sum(sii.qty)) as deployed_qty from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code join `tabCustomer` as c on c.name=si.customer where si.company="Omnipresent Services" and si.status!='Cancelled' and si.status!="Draft" and c.customer_status!="Closed"  and i.brand=%(brand)s group by si.customer,i.item_name) as meta where meta.deployed_qty!=0 """,values=values,as_dict=True)