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
		items_list=frappe.db.sql("""select i.brand,cb.item_code,i.item_name,(if (sale.bill_qty is null ,0,sale.bill_qty) ) -(if (sale.sale_qty is null,0,sale.sale_qty)) as 'expected' from `tabCustomer Bin` as cb left join (select si.customer,sii.item_code,(select sum(SII.qty) from `tabSales Invoice` as SI join `tabSales Invoice Item` as SII on SI.name=SII.parent where SI.docstatus=1 and SI.company='Omnipresent Services' and si.customer=SI.customer and sii.item_code=SII.item_code) as bill_qty,(select sum(qty) from `tabDay Wise Sales` as dws where dws.customer=si.customer and dws.item_code=sii.item_code) as sale_qty from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on sii.parent=si.name where si.docstatus=1 and si.company='Omnipresent Services' and si.customer=%(customer)s group by si.customer,sii.item_code) as sale on sale.item_code=cb.item_code and sale.customer=cb.customer join `tabItem` as i on i.item_code=cb.item_code where cb.customer=%(customer)s and i.item_group=%(item_group)s order by i.brand""",values={'customer':self.customer,'item_group':self.item_group},as_list=True)
		items_list.sort(key=lambda x: (x[3]==0,x[0],x[2]))
		for item in items_list:
			self.append('items',
						{'item_code' : item[1], 
						'item_name' : item[2],
						'last_visit_qty': item[3],
						'brand': item[0],
						'current_available_qty' : item[3]})
	@frappe.whitelist()
	def fetch_difference_item(self):
		difference=3
		message="""Please recheck with the store for the following items   """
		is_difference_found=False
		for item in self.items:
			if difference<=item.last_visit_qty-item.current_available_qty:
				is_difference_found=True
				message+=f"\n   # {item.item_name} ,   "
		if is_difference_found:
			return message
		return "False"