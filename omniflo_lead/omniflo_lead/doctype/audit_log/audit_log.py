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
