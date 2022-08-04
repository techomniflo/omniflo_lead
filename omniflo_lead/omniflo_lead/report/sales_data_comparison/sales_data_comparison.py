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
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,ali.item_name,i.brand from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.brand from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.`status` != 'Cancelled' and si.`status`!="Draft" and si.`status` != 'Return' order by si.posting_date;""",values=values,as_dict=True)

	return_data=frappe.db.sql("""select (select (DATE_FORMAT(SI.posting_date,'%%d-%%m-%%y')) as date from `tabSales Invoice` as SI where SI.name=si.return_against) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.brand from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.`status` = 'Return' order by date;""",values=values,as_dict=True)

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
				if customer not in customer_dict:
					customer_dict[customer]={item_name:[qty,brand]}
				else:
					if item_name not in customer_dict[customer]:
						customer_dict[customer][item_name]=[qty,brand]
					
					else:
						if is_add==True:
							customer_dict[customer][item_name][0]+=qty
		return customer_dict

	def get_dictionary_with_date(data,is_add=None):
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
	#pprint.pprint(final_dictionary)
	dates=list(final_dictionary.keys())
	dates.sort(key=lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
	previous={}
	sales=[]
	for i in dates:
		customers=list(final_dictionary[i].keys())
		for customer in customers:
			if customer in previous:
				items_in_final=list(final_dictionary[i][customer].keys())
				for item in items_in_final:
					if item in previous[customer]:
						temp=[]
						temp.append(i)
						temp.append(customer)
						temp.append(item)
						if (previous[customer][item][0]-final_dictionary[i][customer][item][0])>0:
							temp.append(previous[customer][item][0]-final_dictionary[i][customer][item][0])
							temp.append(final_dictionary[i][customer][item][1])
							temp.append(final_dictionary[i][customer][item][1])
							sales.append(temp)
					previous[customer][item]=final_dictionary[i][customer][item]
			previous[customer]=copy.deepcopy(final_dictionary[i][customer])
	sales_on_customer={}
	sales_on_date={}
	# pprint.pprint(sales)
	for i in sales:
		if i[0] not in sales_on_date:
			print(i[0])
			sales_on_date[i[0]]={i[2]:i[3]}
		else:
			if i[2] not in sales_on_date[i[0]]:
				sales_on_date[i[0]][i[2]]=i[3]
			else:
				sales_on_date[i[0]][i[2]]+=i[3]
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
	return sales_comparision_data
		
