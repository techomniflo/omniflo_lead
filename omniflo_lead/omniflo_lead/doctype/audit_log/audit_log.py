# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
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

	@frappe.whitelist()
	def fetch_items(self):
		bin_items = frappe.get_all('Customer Bin', filters = {'customer' : self.customer}, fields =['name'])
		for item in bin_items:
			customer_bin = frappe.get_doc('Customer Bin', item['name'])
			self.append('items',
						{'item_code' : customer_bin.item_code , 
						'last_visit_qty': customer_bin.available_qty, 
						'current_available_qty' : customer_bin.available_qty})
