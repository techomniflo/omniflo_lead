# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

# import frappe
import frappe
import requests
import pprint
import json
from dateutil import parser
import pprint
from datetime import datetime

def execute(filters=None):
	columns=["Date","Customer","QTY","Item_Name","Brand","sales_from"]
	return columns, calculate_sales()

def process_data():
	tx = []
	items = set()
	stores = set()
	def process_promoter():
		promoter_data=frappe.db.sql("""select psc.brand,psc.customer,psc.qty,psc.creation as date,psc.item_name,(select i.name from `tabItem` as i where i.item_name=psc.item_name and i.brand=psc.brand and psc.brand!='Nutriorg' and name is not null) as item_code from `tabPromoter Sales Capture` as psc  where psc.brand!="Nutriorg" group by date(psc.creation),psc.customer,psc.item_name""",as_dict=True)
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
		sales_data=frappe.db.sql("""select ADDTIME(CONVERT(si.posting_date, DATETIME), si.posting_time) as date,i.brand,si.customer as customer,sii.qty,i.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.`status` != 'Cancelled' and si.`status`!="Draft" order by si.posting_date;""",as_dict=True)
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
		# headers={"Authorization":"Token 0d7714235220ffb:681cc4ece6e4700"}
		# url="http://engine-staging-1011.omniflo.in/api/method/omniflo_lead.omniflo_lead.api.frappe_api.audit_data"
		# headers={"Authorization":"Token 0d7714235220ffb:681cc4ece6e4700"}
		audit_data=frappe.db.sql("""select al.posting_date as date,al.customer,ali.current_available_qty as qty,i.item_name,i.mrp,i.brand from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where al.docstatus=1 order by al.posting_date;""",as_dict=True)
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
			customer, brand, item, qty, date = tx['customer'], tx['brand'], tx['item_name'], tx['qty'], tx['dt']
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
				stock[customer][brand][item].append({'date':date, 'billed_qty': billed_qty, 'current_qty': current_qty, 'cumulative_sales': cumulative_sales,'event_type': 'invoice'})
		
		if tx['event_type'] == 'audit' :
			customer, brand, item, qty, date = tx['customer'], tx['brand'], tx['item_name'], tx['qty'], tx['dt']
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
				stock[customer][brand][item].append({'date':date, 'billed_qty': billed_qty, 'current_qty': current_qty,'cumulative_sales': cumulative_sales, 'event_type': 'audit'})
		
		if tx['event_type'] == 'promoter' :
			customer, brand, item, qty, date = tx['customer'], tx['brand'], tx['item_name'], tx['qty'], tx['dt']
			
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
					if min_possible_sales > item[i-1]['cumulative_sales'] and min_possible_sales > 0:
						sales = min_possible_sales - item[i-1]['cumulative_sales']
						min_possible_sales = item[i-1]['cumulative_sales']
						date, event_type = item[i]['date'], item[i]['event_type']
						sale_events.append((date, customer, sales, sku, brand, event_type))
	sale_events = sorted(sale_events, key=lambda d: d[0])
	for i in range(len(sale_events)):
		sale_events[i]=list(sale_events[i])
		sale_events[i][0]=sale_events[i][0].strftime("%d-%m-%y")
	return sale_events
