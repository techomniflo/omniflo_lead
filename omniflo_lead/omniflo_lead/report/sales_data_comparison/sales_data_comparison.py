# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
import json
import time
import datetime
import copy
from collections import defaultdict


def execute(filters=None):

	columns=["customer","brand","item_name","Bill_Qty","Store_Qty","sales_from_invoices:","sales_from_audit/stock","Difference Found"]
	
	return columns,comparison_data_of_invoice_and_gmv()

@frappe.whitelist()
def comparison_data_of_invoice_and_gmv():
	values={}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,i.item_name,i.brand,i.mrp,i.item_code from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,i.item_name,i.brand,i.mrp,i.item_code from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.`status` != 'Cancelled' and si.`status`!="Draft" order by si.posting_date;""",values=values,as_dict=True)

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
				brand=x[i]['brand']
				mrp=x[i]['mrp']
				if customer not in customer_dict:
					customer_dict[customer]={item_name:[qty,brand,mrp]}
				else:
					if item_name not in customer_dict[customer]:
						customer_dict[customer][item_name]=[qty,brand,mrp]
					
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

				if (cumulative_sales_with_date[i][customer][item][0]-sales_recorder[customer][item][0]) > 0:
					diff=cumulative_sales_with_date[i][customer][item][0]-sales_recorder[customer][item][0]
					sales.append([i,customer,item,diff,cumulative_sales_with_date[i][customer][item][1],cumulative_sales_with_date[i][customer][item][2]])

				count+=cumulative_sales_with_date[i][customer][item][0]-sales_recorder[customer][item][0]
				sales_recorder[customer][item] = copy.deepcopy(cumulative_sales_with_date[i][customer][item])
	sales_on_customer={}
	for i in sales:
		if i[1] not in sales_on_customer:
			sales_on_customer[i[1]]={i[2]:i[3]}
		else:
			if i[2] not in sales_on_customer[i[1]]:
				sales_on_customer[i[1]][i[2]]=i[3]
			else:
				sales_on_customer[i[1]][i[2]]+=i[3]
	# return sales_on_customer
	sales_from_invoices=frappe.db.sql("""select si.customer_name as customer,i.brand,i.item_name,(sum(sii.qty)) as Bill_Qty,(select available_qty from `tabCustomer Bin` as cb join `tabItem` as ii on cb.item_code=ii.item_code where cb.customer=si.customer and ii.item_code=i.item_code) as Store_Qty from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code where si.company="Omnipresent Services" and si.status!='Cancelled' and si.status!="Draft" group by i.brand,si.customer,i.item_name;""",as_dict=True)
	#return sales_from_invoices
	sales_comparision_data=[]
	for i in sales_from_invoices:
		temp=[]
		temp.append(i['customer'])
		if i['brand']==None or i['brand']=='null':
			temp.append("Null")
		else:
			temp.append(i['brand'])
		temp.append(i['item_name'])
		temp.append(i['Bill_Qty'])
		temp.append(i['Store_Qty'])
		temp.append(i['Bill_Qty']-i['Store_Qty'])
		if i['customer'] in sales_on_customer:
			if i['item_name'] in sales_on_customer[i['customer']]:
				temp.append(sales_on_customer[i['customer']][i['item_name']])
			else:
				temp.append(0)
		else:
			temp.append(0)
		temp.append(temp[-2]-temp[-1])
		sales_comparision_data.append(temp)
	sales_comparision_data.sort(lambda x:(x[7],x[0],x[1]))
	return sales_comparision_data