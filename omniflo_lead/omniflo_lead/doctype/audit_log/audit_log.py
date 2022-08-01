# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
import json
import time
import datetime
import copy
from frappe.model.document import Document

class AuditLog(Document):
	def validate(self):
		pass

	def before_save(self):
		pass

	def on_submit(self):


		self.update_bin()
		try:
			customer_doc = frappe.get_doc('Customer', self.customer)
			if not customer_doc.latitude:
				customer_doc.latitude = self.latitude
			if not customer_doc.longitude:
				customer_doc.longitude = self.longitude
			customer_doc.save()
		except:
			pass

		self.send_mail_if_sales_not_match()
	def send_mail_if_sales_not_match(self):
		msg=[]
		is_send_mail=False
		if is_ignored_customer(self.customer):
			is_send_mail=False
		elif is_get_difference_on_item(self.customer)!=False:
			msg.append(is_get_difference_on_item(self.customer))
			msg.append(total_sales_from_gmv(self.customer))
			is_send_mail=True
		if is_send_mail:
			message=json.dumps(msg, indent = 4)
			recipients=["raghav@omniflo.in","operations@omniflo.in","gourav.saini@omniflo"]
			title="Check audit for "+str(self.customer)
			sendmail(self,[recipients],message,title)
		return

	def update_bin(self):
		for item in self.items:
			customer_bin = frappe.db.get_value('Customer Bin', {'customer': self.customer, 'item_code': item.item_code})
			if not customer_bin:
				customer_bin = frappe.new_doc('Customer Bin')
				customer_bin.customer = self.customer
				customer_bin.item_code = item.item_code
				customer_bin.available_qty = item.current_available_qty
				customer_bin.save(ignore_permissions = True)
				continue
			else:
				customer_bin = frappe.get_doc('Customer Bin', customer_bin)
				customer_bin.available_qty = item.current_available_qty
				customer_bin.save(ignore_permissions = True)

	def on_cancel(self):
		audit_last_doc=frappe.get_last_doc('Audit Log',{'customer': self.customer})
		if not audit_last_doc:
			pass
		else:
			if audit_last_doc.name==self.name:
				for item in audit_last_doc.items:
					customer_bin = frappe.db.get_value('Customer Bin', {'customer':self.customer, 'item_code': item.item_code})
					if not customer_bin:
						customer_bin = frappe.new_doc('Customer Bin')
						customer_bin.customer = audit_last_doc.customer
						customer_bin.item_code = item.item_code
						customer_bin.available_qty = item.last_visit_qty
						customer_bin.save(ignore_permissions = True)
					else:
						customer_bin = frappe.get_doc('Customer Bin', customer_bin)
						customer_bin.available_qty = item.last_visit_qty
						customer_bin.save(ignore_permissions = True)
 
	@frappe.whitelist()
	def fetch_items(self):
		bin_items = frappe.get_all('Customer Bin', filters = {'customer' : self.customer}, fields =['name'])
		current_items = []
		if self.get('items'):
			current_items = [item.item_code for item in self.get('items')]
		for item in bin_items:
			customer_bin = frappe.get_doc('Customer Bin', item['name'])
			if customer_bin.item_code in current_items:
				continue

			item_doc = frappe.get_doc('Item', customer_bin.item_code)
			self.append('items',
						{'item_code' : customer_bin.item_code , 
						'item_name' : item_doc.item_name,
						'last_visit_qty': customer_bin.available_qty, 
						'current_available_qty' : customer_bin.available_qty})

def sendmail(doc,recipients,msg,title,attachments=None):
	email_args = {
		'recipients':recipients,
		'message':msg,
		'subject':title,
		'reference_doctype':doc.doctype,
		'reference_name':doc.name
	}

	if attachments:email_args['attachments']=attachments

	#send mail
	frappe.enqueue(method=frappe.sendmail,queue='short',timeout=300,is_async=True,**email_args)

def is_get_difference_on_item(customer):
	values={'customer':customer}
	difference_on_item=["difference_found_on_items"]
	sales_from_gmv=total_sales_from_gmv(customer)[3]
	item_sale_dictionary=frappe.db.sql("""select i.item_name,(sum(sii.qty)) as Bill_Qty,(select available_qty from `tabCustomer Bin` as cb join `tabItem` as ii on cb.item_code=ii.item_code where cb.customer=si.customer and ii.item_code=i.item_code) as Store_qty from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code where si.company="Omnipresent Services" and si.status!='Cancelled' and si.status!="Draft" and si.customer=%(customer)s group by i.brand,si.customer,i.item_name;""",values=values,as_dict=True)

	for i in item_sale_dictionary:
		if i["item_name"] in sales_from_gmv:
			difference=i["Bill_Qty"]-i["Store_qty"]
			if difference!=sales_from_gmv[i["item_name"]]:
				msg={}
				msg["item_name"]=i["item_name"]
				msg["Sales_from_Billing"]=difference
				msg["Sales_from_gmv"]=sales_from_gmv[i["item_name"]]
				msg["difference"]=difference-sales_from_gmv[i["item_name"]]
				difference_on_item.append(msg)
	if len(difference_on_item)>1:
		return difference_on_item
	else:
		return False
def is_ignored_customer(customer):
	values={"customer":customer}
	data=frappe.db.sql("""select distinct si.customer from `tabSales Invoice` as si where si.status!="Draft" and si.status!="Cancelled" and si.company="Omnipresent Services" and si.customer=%(customer)s ;""",values=values,as_list=True)
	return len(data)!=1


 
def total_sales_from_gmv(customer):
	values={"customer":customer}
	audit_data=frappe.db.sql("""select (DATE_FORMAT(al.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=al.customer) as customer,ali.current_available_qty as qty,ali.item_name,i.brand from `tabAudit Log` as al join `tabAudit Log Items` as ali on ali.parent=al.name join `tabItem` as i on i.item_code=ali.item_code 
				where al.customer=%(customer)s and al.docstatus=1 order by al.posting_date;""",values=values,as_dict=True)
	sales_data=frappe.db.sql("""select (DATE_FORMAT(si.posting_date,'%%d-%%m-%%y')) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.brand from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.customer=%(customer)s and si.`status` != 'Cancelled' and si.`status`!="Draft" and si.`status` != 'Return' order by si.posting_date;""",values=values,as_dict=True)

	return_data=frappe.db.sql("""select (select (DATE_FORMAT(SI.posting_date,'%%d-%%m-%%y')) as date from `tabSales Invoice` as SI where SI.name=si.return_against) as date,(select c.customer_name from `tabCustomer` as c where c.name=si.customer) as customer,sii.qty,sii.item_name,i.brand from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name join `tabItem` as i on i.item_code=sii.item_code 
				where si.customer=%(customer)s and si.`status` = 'Return' order by date;""",values=values,as_dict=True)

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
				customer=x[i]['brand']
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
							sales.append([current,customer,item,difference])
	sales_on_dates={}
	sales_on_brand={}
	sales_on_items={}
	count=0
	for i in sales:
		if i[3]>0:
			if i[0] not in sales_on_dates:
				sales_on_dates[i[0]]={i[2]:i[3]}
			else:
				if i[2] not in sales_on_dates[i[0]]:
					sales_on_dates[i[0]][i[2]]=i[3]
				else:
					sales_on_dates[i[0]][i[2]]=sales_on_dates[i[1]][i[2]]+i[3]

			if i[1] not in sales_on_brand:
				sales_on_brand[i[1]]={i[2]:i[3]}
			else:
				if i[2] not in sales_on_brand[i[1]]:
					sales_on_brand[i[1]][i[2]]=i[3]
				else:
					sales_on_brand[i[1]][i[2]]=sales_on_brand[i[1]][i[2]]+i[3]
			if i[2] not in sales_on_items:
				sales_on_items[i[2]]=i[3]
			else:
				sales_on_items[i[2]]=sales_on_items[i[2]]+i[3]
			count+=i[3]
		
	return [{"Total":count},sales_on_brand,sales_on_dates,sales_on_items]
