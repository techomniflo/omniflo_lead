import frappe
import json
import time
import datetime
import copy
from collections import defaultdict

@frappe.whitelist()
def audit():
	values={"brand":frappe.request.args["brand"]}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,ali.item_name,i.mrp from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where i.brand=%(brand)s and al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
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
	return audit_dictionary


@frappe.whitelist()
def sales():
	values={"brand":frappe.request.args["brand"]}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,ali.item_name,i.mrp from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where i.brand=%(brand)s and al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
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
	sales_dictionary=get_dictionary_with_date(sales_data)
	return sales_dictionary

