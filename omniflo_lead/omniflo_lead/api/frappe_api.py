import frappe
import json
import time
import datetime
import copy
from collections import defaultdict

@frappe.whitelist()
def login():
	"""" This is to verify the credential for omniverse. """
	user=frappe.request.args["user"]
	password=frappe.request.args["password"]
	try:
		doc=frappe.get_doc('Omniverse Brand Credential',user)
	except:
		frappe.local.response['http_status_code'] = 404
		return
	if doc.get_password('password')==password:
		return {'brand':doc.brand,'validate':True}
	frappe.local.response['http_status_code'] = 401
	return

@frappe.whitelist(allow_guest=True)
def is_active_brand():
	""" This function return the is that brand is active or not. """
	try:
		brand=frappe.request.args["brand"]
		doc=frappe.get_doc('Omniverse Brand Credential',brand)
	except:
		return False
	return doc.disabled==0

#Gives total no live store of perticular brand -> int(number)
@frappe.whitelist()
def total_live_store():
    values={"brand":frappe.request.args["brand"]}
    count_of_store = frappe.db.sql("""
		select count(*) from (
			select distinct meta.customer from  
				(
					select si.customer,sum(sii.qty) as billed_qty ,(select sum(cb.available_qty) from `tabCustomer Bin` as cb join `tabItem` as I on I.item_code=cb.item_code where I.brand=i.brand and cb.customer=si.customer and I.item_group!='Sample') as available_qty from `tabSales Invoice` as si  join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code join `tabCustomer` as c on c.name=si.customer where i.brand=%(brand)s and si.docstatus=1 and c.customer_status='Live' group by si.customer ) as meta where meta.billed_qty>0 and meta.available_qty>0

				union
			
			select distinct tpi.customer from `tabThird Party Invoicing` as tpi join `tabThird Party Invoicing Item` as  tpii on tpi.name=tpii.parent join `tabItem` as i on i.item_code=tpii.item_code join `tabCustomer` as c  on c.name=tpi.customer join `tabCustomer Bin` as cb on cb.customer=c.name and i.item_code=cb.item_code  where c.customer_status='Live' and i.brand=%(brand)s and cb.available_qty>0 and i.item_group!='Sample' ) as no_store
    """,values=values,as_list=True)
    return count_of_store


#it gives list of stores with their id and name
@frappe.whitelist()
def stores_lives():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql(""" select distinct cb.customer,c.customer_name,c.customer_id from `tabCustomer Bin` as cb join `tabItem` as i on i.name=cb.item_code join `tabCustomer` as c on c.name=cb.customer where i.brand=%(brand)s and cb.available_qty!=0 and c.customer_status='Live' and i.item_group!='Sample' """,values=values,as_dict=True)

#Gives total no of live inventory for perticular brand
@frappe.whitelist()
def total_inventory():
	values={"brand":frappe.request.args["brand"]}

	total_inventory=frappe.db.sql("""select 
										sum(cb.available_qty) 
										from 
										`tabCustomer Bin` as cb 
										join `tabItem` as i on i.item_code = cb.item_code 
										where 
										cb.available_qty > 0 
										and i.brand = %(brand)s 
										and i.item_group != 'Sample'
							   """,values=values,as_list=True)
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
	values={"brand":'%'+frappe.request.args["brand"]+'%'}
	return frappe.db.sql(""" with cte as (

									select al.posting_date as image_date,al.customer,c.customer_id,c.customer_name,(select cp.name1 from `tabCustomer Profile` as cp where cp.customer=al.customer) as google_name,ald.image,ald.item_code as image_type,ald.status from `tabAudit Log Details` as ald join `tabAudit Log` as al on al.name=ald.parent join `tabCustomer` as c on c.name=al.customer where status='Approve'  and approved_brand is not null and approved_brand LIKE %(brand)s
									union
									select osi.creation as image_date,osi.customer,c.customer_id,c.customer_name,(select cp.name1 from `tabCustomer Profile` as cp where cp.customer=c.name) as google_name,osii.image,osii.type as image_type,osii.status from `tabOmniverse Store Image` as osi join `tabOmniverse Store Image Items` as osii on osi.name=osii.parent left join `tabCustomer` as c on c.name=osi.customer where osii.image is not null and osii.`status`='Approve' and osii.approved_brand LIKE %(brand)s
         								) 
							select * from cte where cte.image_date in ( select max(m.image_date) from cte as m where m.customer=cte.customer and m.image_type=cte.image_type )
       					""",values=values,as_dict=True)

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

@frappe.whitelist(allow_guest=True)
def promoter_data():
	return frappe.db.sql("""select psc.customer,psc.brand,psc.qty,psc.creation as date,psc.item_code,psc.item_name,psc.age,psc.gender  from `tabPromoter Sales Capture` as psc where psc.item_code is not null  order by psc.creation""",as_dict=True)

@frappe.whitelist(allow_guest=True)
def sales_data():
	return frappe.db.sql("""select ADDTIME(CONVERT(si.posting_date, DATETIME), si.posting_time) as date,i.brand,si.customer as customer,sii.qty,i.item_name,i.mrp,i.item_code,null as age,null as gender from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
					where si.docstatus=1 and i.item_group!='Sample' order by si.posting_date;""",as_dict=True)

@frappe.whitelist(allow_guest=True)
def audit_data():
	return frappe.db.sql("""select al.posting_date as date,al.customer,ali.current_available_qty as qty,i.item_code,i.item_name,i.mrp,i.brand,null as age,null as gender from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
					where al.docstatus=1 and i.item_group!='Sample' order by al.posting_date;""",as_dict=True)

@frappe.whitelist()
def warehouse_quantity():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("""select i.item_name,i.sub_brand,i.brand,i.item_code,b.actual_qty as qty from `tabBin` as b join `tabItem` as i on i.item_code=b.item_code where b.warehouse="Kormangala WareHouse - OS" and i.brand=%(brand)s and i.item_group!='Sample'  """,values=values,as_dict=True)

@frappe.whitelist()
def deployed_quantity():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("""select c.customer_name,c.customer_id,cb.customer ,i.item_name,i.item_code,i.sub_brand,i.brand,cb.available_qty as qty from `tabCustomer Bin` as cb join `tabItem` as i on i.name=cb.item_code join `tabCustomer` as c on c.name=cb.customer where i.brand=%(brand)s and cb.available_qty>0 and c.customer_status='Live' and i.item_group!='Sample' """,values=values,as_dict=True)

@frappe.whitelist()
def customer_profile():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("""
		      
		select meta.customer,meta.asset_configuration,c.customer_name,c.customer_id,if(meta.available_qty<=0 and c.customer_status='Live','Dormant',c.customer_status) as customer_status,meta.start_date,cp.name1 as google_name,cp.sub_type,cp.address,cp.link as map_link,cp.image_url,cp.latitude,cp.longitude,cp.rating,cp.review_count,cp.store_timings,cp.daily_footfall,cp.delivery,cp.number_of_aisles_inside_the_store as asile,cp.number_of_floors,cp.average_order_value,cp.brand_present,cp.locality_area,cp.type,cp.brand_priority,cp.area,cp.number_of_floors from (
					select distinct si.customer,min(si.posting_date) as start_date,(select sum(cb.available_qty) from `tabCustomer Bin` as cb join `tabItem` as I on cb.item_code=I.item_code where si.customer=cb.customer and I.brand=i.brand ) as available_qty,( select GROUP_CONCAT(distinct p.asset_configuration) from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent where p.disabled=0 and pi.brand=i.brand and p.customer=si.customer ) as asset_configuration from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code where i.brand=%(brand)s and si.docstatus=1 group by si.customer
						union
					select distinct tpi.customer,min(date(tpi.posting_date)) as start_date,(select sum(cb.available_qty) from `tabCustomer Bin` as cb join `tabItem` as I on cb.item_code=I.item_code where tpi.customer=cb.customer and I.brand=i.brand) as available_qty,( select GROUP_CONCAT(distinct p.asset_configuration) from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent where p.disabled=0 and pi.brand=tpii.brand and p.customer=tpi.customer ) as asset_configuration from `tabThird Party Invoicing` as tpi join `tabThird Party Invoicing Item` as tpii on tpi.name=tpii.parent join `tabItem` as i on i.item_code=tpii.item_code where i.brand=%(brand)s and tpi.docstatus=1 group by tpi.customer ) as meta
					
				left join `tabCustomer` as c on c.name=meta.customer left join `tabCustomer Profile` as cp on cp.customer=c.name			

			""",values=values,as_dict=True)

@frappe.whitelist()
def calculate_gmv():
	
	def process_data():
		
		tx = []
		items = set()
		stores = set()
		def process_promoter():
			values={"brand":frappe.request.args["brand"]}
			promoter_data=frappe.db.sql("""select psc.customer,psc.brand,psc.qty,psc.creation as date,psc.item_code,psc.item_name  from `tabPromoter Sales Capture` as psc where psc.item_code is not null and psc.brand=%(brand)s  order by psc.creation""",values=values,as_dict=True)
			entries = promoter_data
			#{'brand': 'Brawny Bear', 'customer': 'bangalore-rice-traders', 'date': '2022-10-20 22:40:14.433979', 'item_name': 'Date Sugar 200g', 'item_code': 'OMNI-ITM-BBR-078', 'qty': 2.0}
			for entry in entries:
				# try:
				# 	dt = parser.parse(entry['date'])
				# except:
					# frappe.msgprint(json.dumps(entry['date'],default=str))
				entry['event_type']='promoter'
				entry['dt'] = entry['date']
				tx.append(entry)


		def process_invoice():
			values={"brand":frappe.request.args["brand"]}
			sales_data=frappe.db.sql("""select ADDTIME(CONVERT(si.posting_date, DATETIME), si.posting_time) as date,i.brand,si.customer as customer,sii.qty,i.item_name,i.mrp,i.item_code from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
					where si.`status` != 'Cancelled' and si.`status`!="Draft" and i.brand=%(brand)s order by si.posting_date;""",values=values,as_dict=True)
			entries = sales_data
			#{'date': '2022-05-30 15:34:34', 'brand': 'Spice Story', 'customer': 'Royal villas super market', 'qty': 2.0, 'item_name': 'Schezwan Chutney', 'mrp': '125'}
			for entry in entries:
				dt = entry['date']
				entry['event_type']='invoice'
				entry['dt'] = dt
				tx.append(entry)
				items.add((entry['brand'], entry['item_name'], float(entry['mrp'])))
				stores.add(entry['customer'])

		def process_audit():
			values={"brand":frappe.request.args["brand"]}
			audit_data=frappe.db.sql("""select al.posting_date as date,al.customer,ali.current_available_qty as qty,i.item_code,i.item_name,i.mrp,i.brand from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
					where al.docstatus=1 and i.brand=%(brand)s order by al.posting_date;""",values=values,as_dict=True)
			entries =audit_data
			#{'date': '2021-11-29 00:00:00', 'customer': 'Nut Berry Akshay Nagar', 'qty': 1.0, 'item_name': 'Rage Coffee 50GMS Chai Latte', 'mrp': '349', 'brand': 'Rage Coffee'}
			for entry in entries:
				dt = entry['date']
				entry['event_type']='audit'
				entry['dt'] = dt
				tx.append(entry)


		process_promoter()
		process_invoice()
		process_audit()
		tx = sorted(tx, key=lambda d: d['dt']) 
		return items, stores, tx
	
	def stock_position():
		items, stores, txs = process_data()
		stock = {}
		for tx in txs:
			if tx['event_type'] == 'invoice' :
				customer, brand, item, qty, date = tx['customer'], tx['brand'], tx['item_code'], tx['qty'], tx['dt']
				if customer not in stock:
					stock[customer] = {}
				if brand not in stock[customer]:
					stock[customer][brand] = {}
				if item not in stock[customer][brand]:
					stock[customer][brand][item] = []
				if not stock[customer][brand][item]:
					stock[customer][brand][item].append({'date':date, 'billed_qty': qty, 'current_qty': qty, 'cumulative_sales': 0, 'event_type': 'invoice'})
				else:
					current_qty = qty + stock[customer][brand][item][-1]['current_qty']
					billed_qty = qty + stock[customer][brand][item][-1]['billed_qty']
					cumulative_sales = billed_qty - current_qty
					if current_qty < 0:
						cumulative_sales = billed_qty
					stock[customer][brand][item].append({'date':date, 'billed_qty': billed_qty, 'current_qty': current_qty, 'cumulative_sales': cumulative_sales,'event_type': 'invoice'})
			
			if tx['event_type'] == 'audit' :
				customer, brand, item, qty, date = tx['customer'], tx['brand'], tx['item_code'], tx['qty'], tx['dt']
				if customer not in stock:
					stock[customer] = {}
				if brand not in stock[customer]:
					stock[customer][brand] = {}
				if item not in stock[customer][brand]:
					stock[customer][brand][item] = []
				if not stock[customer][brand][item]:
					stock[customer][brand][item].append({'date':date, 'billed_qty': 0, 'current_qty': qty, 'cumulative_sales': 0, 'event_type': 'audit'})
				else:
					billed_qty = stock[customer][brand][item][-1]['billed_qty']
					current_qty = qty
					cumulative_sales = billed_qty - current_qty
					if current_qty < 0:
						cumulative_sales = billed_qty
					stock[customer][brand][item].append({'date':date, 'billed_qty': billed_qty, 'current_qty': current_qty,'cumulative_sales': cumulative_sales, 'event_type': 'audit'})
			
			if tx['event_type'] == 'promoter' :
				customer, brand, item, qty, date = tx['customer'], tx['brand'], tx['item_code'], tx['qty'], tx['dt']
				
				if customer not in stock:
					continue
				if brand not in stock[customer]:
					continue
				if item not in stock[customer][brand]:
					continue
				if not stock[customer][brand]:
					continue
				else:
					billed_qty = (stock[customer][brand][item][-1]['billed_qty'])
					current_qty = (stock[customer][brand][item][-1]['current_qty']) - (qty)
					cumulative_sales = billed_qty - current_qty
					if current_qty < 0:
						cumulative_sales = billed_qty
					stock[customer][brand][item].append({'date':date, 'billed_qty': billed_qty, 'current_qty': current_qty, 'cumulative_sales': cumulative_sales, 'event_type': 'promoter'})
		
		return stock

	

	@frappe.whitelist()      
	def calculate_sales():
		stock = stock_position()
		sale_events = []
		for customer in stock:
			for brand in stock[customer]:
				for sku in stock[customer][brand]:
					item = stock[customer][brand][sku]
					min_possible_sales = item[-1]['cumulative_sales']
					for i in range(len(item)-1, 0, -1): #python reverse loop until second last element
						if min_possible_sales > item[i-1]['cumulative_sales'] and min_possible_sales > 0 and item[i-1]['cumulative_sales']>=0:
							sales = min_possible_sales - item[i-1]['cumulative_sales']
							min_possible_sales = item[i-1]['cumulative_sales']
							date, event_type = item[i]['date'], item[i]['event_type']
							sale_events.append((date, customer, sales, sku, brand, event_type))
		sale_events = sorted(sale_events, key=lambda d: d[0])
		return sale_events
		
	def return_sales():
		values={"brand":frappe.request.args["brand"]}
		rv=frappe.db.sql("""select i.item_code,i.item_name,i.mrp from `tabItem` as i where i.brand=%(brand)s""",values=values,as_dict=True)
		item={}
		for i in rv:
			if i['item_code'] not in item:
				item[i['item_code']]=[i['item_name'],i['mrp']]
		sale_events=calculate_sales()
		for i in range(len(sale_events)):
			sale_events[i]=list(sale_events[i])
			sale_events[i][0]=sale_events[i][0].strftime("%d-%m-%y")
			item_code=sale_events[i][3]
			if item_code in item:
				sale_events[i].append(item[item_code][0])
				sale_events[i].append(float(item[item_code][1])*sale_events[i][2])
			
		return sale_events
	return json.loads(json.dumps(return_sales(),default=str))


@frappe.whitelist()
def age_and_gender():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("""select date(psc.creation) as date,psc.customer,psc.item_code,psc.item_name,psc.gender,psc.age,psc.qty from `tabPromoter Sales Capture` as psc where psc.gender is not null and psc.brand=%(brand)s and psc.item_code is not null ;""",values=values,as_dict=True)

@frappe.whitelist()
def calculate_sales_date_wise():
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("""select DATE_FORMAT(dws.date,'%%d-%%m-%%y') as date ,dws.customer,dws.qty,dws.item_code,i.brand,i.sub_brand,dws.sale_from,i.item_name,(dws.mrp*dws.qty) as gmv,dws.age,dws.gender,c.customer_id from `tabDay Wise Sales` as dws join `tabItem` as i on i.name=dws.item_code join `tabCustomer` as c on c.name=dws.customer where i.brand=%(brand)s order by dws.date """,values=values,as_dict=True)

@frappe.whitelist()
def item():
	""" This API provides item details such as item code, name, MRP, and GST HSN code. """
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql(""" select i.item_code,i.item_name,i.mrp,i.gst_hsn_code from `tabItem` as i where i.brand=%(brand)s and i.item_group!='Sample' """,values=values,as_dict=True)

@frappe.whitelist()
def platform_sales_invoice():
	""" This API provides details of invoices raised against the brand. """
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql(""" select si.name as invoice_id,si.posting_date,si.outstanding_amount,si.due_date,si.net_total,si.total_taxes_and_charges,si.apply_discount_on,si.discount_amount,si.grand_total,si.rounding_adjustment,si.rounded_total from `tabSales Invoice` as si where si.docstatus=1 and si.company='Omniway Technologies Pvt Ltd' and si.customer in ( select brl.customer from `tabBrand Reference Links` as brl where brl.parent = %(brand)s and brl.party_type='Customer' ) """,values=values,as_dict=True)

@frappe.whitelist()
def item_billed_to_store():
	""" This API provides a list of items sent to customers, including customer name and date,gmv. """
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql(""" select sum(sii.qty*sii.conversion_factor*i.mrp) as gmv from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code where si.docstatus=1 and i.brand=%(brand)s and i.item_group!='Sample'  """,values=values,as_list=True)

@frappe.whitelist()
def brand_message():
	""" This API shows brand messages. """
	values={"brand":frappe.request.args["brand"]}
	return frappe.db.sql("select bm.message,bm.type from `tabOmniverse Brand Message` as bm where bm.brand=%(brand)s order by bm.modified desc limit 1",values=values,as_dict=True)

@frappe.whitelist()
def brand_offers(brand:str):
	""" This API provides a list of offers to display in Omniverse. """
	values={"brand":brand}
	return frappe.db.sql(""" select brand,offer from `tabOmniverse Brand Offer` where brand=%(brand)s """,values=values,as_dict=True)

@frappe.whitelist()
def item_send_to_us(brand:str):
	""" This API provides total quantity sent by the brand to omnipresent. """
	values={"brand":brand}
	return frappe.db.sql(""" select sum(pri.received_qty) as qty from `tabPurchase Receipt` as pr join `tabPurchase Receipt Item` as pri on pr.name=pri.parent join `tabItem` as i on i.item_code=pri.item_code where i.brand=%(brand)s and pr.docstatus=1 and i.item_group!='Sample' """,values=values,as_dict=True)