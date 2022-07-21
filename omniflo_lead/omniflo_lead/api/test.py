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


@frappe.whitelist()
def test_time_series_gmv_data():
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
		return customer_dict

	def get_dictionary_with_date(data):
		di={}
		list_of_date=get_date(data)
		for i,date in enumerate(list_of_date):
			di[date]=crate_dict_for_give_date(date,data)
		return di
	audit_dictionary=get_dictionary_with_date(audit_data)
	sales_dictionary=get_dictionary_with_date(sales_data)

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
							sales.append([current,customer,item,difference])
	sales_on_dates={}
	sales_on_customer={}
	count=0
	for i in sales:
		if i[3]>0:
			if i[1] not in sales_on_customer:
				sales_on_customer[i[1]]=i[3]
			else:
				sales_on_customer[i[1]]=sales_on_customer[i[1]]+i[3]

			if i[0] not in sales_on_dates:
				sales_on_dates[i[0]]=i[3]
			else:
				sales_on_dates[i[0]]=sales_on_dates[i[0]]+i[3]
			count+=i[3]
	return [{"Total":count},sales_on_customer,sales_on_dates]



	# it gives time series gmv of audit log+sales invoice
# @frappe.whitelist()
# def time_series_gmv():
# 	values={"brand":frappe.request.args["brand"]}
# 	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,ali.item_name,i.mrp from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
# 				where i.brand=%(brand)s and al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
# 	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
# 				where i.brand=%(brand)s and si.`status` != 'Cancelled' and si.`status`!="Draft" order by si.posting_date;""",values=values,as_dict=True)

# 	#This function gives list of unique date
# 	def get_date(data):
# 		list_of_date=[]
# 		i=0
# 		while i<len(data):
# 			al_date=data[i]['date']
# 			if al_date in list_of_date:
# 				i+=1
# 				continue
# 			else:
# 				list_of_date.append(al_date)
# 				i+=1
# 		return list_of_date



# 	def crate_dict_for_give_date(date,x):
# 		customer_dict={}
# 		date_date=time.strptime(date,"%d-%m-%y")
# 		for i in range(len(x)):
# 			doctype_date=time.strptime(x[i]['date'],"%d-%m-%y")
# 			if date_date==doctype_date:
# 				customer=x[i]['customer']
# 				item_name=x[i]['item_name']
# 				qty=x[i]['qty']
# 				mrp=x[i]['mrp']
# 				if customer not in customer_dict:
# 					customer_dict[customer]={item_name:[qty,mrp]}
# 				else:
# 					if item_name not in customer_dict[customer]:
# 						customer_dict[customer][item_name]=[qty,mrp]
# 		return customer_dict

# 	def get_dictionary_with_date(data):
# 		di={}
# 		list_of_date=get_date(data)
# 		for i,date in enumerate(list_of_date):
# 			di[date]=crate_dict_for_give_date(date,data)
# 		return di
# 	audit_dictionary=get_dictionary_with_date(audit_data)
# 	sales_dictionary=get_dictionary_with_date(sales_data)


# 	#merging audit_dictionary and sales_dictionary
# 	for i in list(audit_dictionary.keys()):
# 		if i not in sales_dictionary:
# 			sales_dictionary[i]=audit_dictionary[i]
# 		else:
# 			customer_list=list(audit_dictionary[i].keys())
# 			for j in customer_list:
# 				if j not in sales_dictionary[i]:
# 					sales_dictionary[i][j]=audit_dictionary[i][j]
# 				else:
# 					item_list=list(audit_dictionary[i][j].keys())
# 					for k in item_list:
# 						if k not in sales_dictionary[i][j]:
# 							sales_dictionary[i][j][k]=audit_dictionary[i][j][k]
# 						else:
# 							sales_dictionary[i][j][k][0]=audit_dictionary[i][j][k][0]


# 	# below that we sort the sales_dictionary according to time
# 	data_keys=list(sales_dictionary.keys())
# 	timestamp_list=[]
# 	for i in data_keys:
# 		d=datetime.datetime.strptime(i,"%d-%m-%y")
# 		timestamp = datetime.datetime.timestamp(d)
# 		timestamp_list.append(timestamp)
# 	timestamp_list.sort()

# 	for j in range(len(timestamp_list)):
# 		convert = datetime.datetime.fromtimestamp(timestamp_list[j])
# 		timestamp_list[j]=convert.strftime("%d-%m-%y")
# 	# new_dictionary contain sorted data according to time
# 	new_dictionary={}
# 	for j in timestamp_list:
# 		new_dictionary[j]=sales_dictionary[j]
# 	return new_dictionary


