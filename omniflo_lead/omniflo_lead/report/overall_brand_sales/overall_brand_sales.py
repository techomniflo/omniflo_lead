# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

# import frappe
import frappe
import json
import time
import datetime
import copy
from collections import defaultdict

def execute(filters=None):
	columns=["Date","Customer","Item_Name","QTY","Brand","Mrp"]
	return columns, Date_wise_sale()
@frappe.whitelist()
def Date_wise_sale():
	values={}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,ali.item_name,i.brand,i.mrp from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.brand,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.`status` != 'Cancelled' and si.`status`!="Draft" and si.`status` != 'Return' order by si.posting_date;""",values=values,as_dict=True)

	return_data=frappe.db.sql("""select (select (DATE_FORMAT(SI.posting_date,'%%d-%%m-%%y')) as date from `tabSales Invoice` as SI where SI.name=si.return_against) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.brand,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.`status` = 'Return' order by date;""",values=values,as_dict=True)

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
	final_time_dictionary={}


	def update_time(date,dic):
		final_time_dictionary[date]=dic

	
	def update_customer(dictionary,date,customer,is_add):
		customer_of_dictionary=[]
		for a in list(dictionary[date].keys()):
			# a refers to customer
			customer_of_dictionary.append(a)
			if a not in customer:
				customer[a]=dictionary[date][a]
				continue
			else:
				if is_add==False:
					customer[a]=dictionary[date][a]
				else:
					#here b refers to items 
					for b in list(dictionary[date][a].keys()):
						if b not in customer[a]:
							customer[a][b]=dictionary[date][a][b]
						else:
							customer[a][b][0]=dictionary[date][a][b][0]+customer[a][b][0]

		new_di={}
		customer_copy=copy.deepcopy(customer)
		# for cu in customer_of_dictionary:
		# 	new_di[cu]=customer_copy[cu]
		update_time(date,customer_copy)
		
		customer=copy.deepcopy(customer_copy)
		return customer
		
	
	
	def merge_dictionary():
		
		customer={}
		i=0
		j=0
		audit_dictionary_date=list(audit_dictionary.keys())
		sales_dictionary_date=list(sales_dictionary.keys())
		sales_dictionary_date.sort(key=lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
		audit_dictionary_date.sort(key=lambda x: datetime.datetime.strptime(x, "%d-%m-%y"))
		while i<len(audit_dictionary_date) and j<len(sales_dictionary_date):
			if datetime.datetime.strptime(audit_dictionary_date[i], "%d-%m-%y") < datetime.datetime.strptime(sales_dictionary_date[j],"%d-%m-%y"):
				date=audit_dictionary_date[i]
				customer=update_customer(audit_dictionary,date,customer,is_add=False)
				i=i+1
			elif datetime.datetime.strptime(audit_dictionary_date[i], "%d-%m-%y") > datetime.datetime.strptime(sales_dictionary_date[j],"%d-%m-%y"):
				date=sales_dictionary_date[j]
				customer=update_customer(sales_dictionary,date,customer,is_add=True)
				j=j+1
			else:
				date=audit_dictionary_date[i]
				customer=update_customer(audit_dictionary,date,customer,is_add=False)
				i=i+1
				j=j+1
		if j<len(sales_dictionary_date):
			while j<len(sales_dictionary_date):
				date=sales_dictionary_date[j]
				customer=update_customer(sales_dictionary,date,customer,is_add=True)
				j=j+1
		else:
			while i<len(audit_dictionary_date):
				date=audit_dictionary_date[i]
				customer=update_customer(audit_dictionary,date,customer,is_add=False)
				i=i+1

	merge_dictionary()
	merged_dictionary=final_time_dictionary
	
	sales=[]
	date=list(merged_dictionary.keys())

	for i in range(1,len(date)):
		previous=date[i-1]
		current=date[i]
		customers=merged_dictionary[current]
		for customer in list(customers.keys()):
			if customer in merged_dictionary[previous]:
				items=merged_dictionary[current][customer]
				for item in list(items.keys()):
					if item in merged_dictionary[previous][customer]:
						if merged_dictionary[current][customer][item][0]!=merged_dictionary[previous][customer][item][0]:
							difference=merged_dictionary[previous][customer][item][0]-merged_dictionary[current][customer][item][0]
							sales.append([current,customer,item,difference,merged_dictionary[current][customer][item][1],merged_dictionary[current][customer][item][2]])
	sales_on_dates={}
	sales_on_customer={}
	sales_on_items={}
	count=0
	list_of_sales=[]
	for i in sales:
		if i[3]>0:
			list_of_sales.append(i)
	return list_of_sales
