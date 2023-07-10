# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ThirdPartyInvoicing(Document):
	def make_customer_bin(self):
		for item in self.item:
			customer_bin = frappe.db.get_value('Customer Bin', {'customer': self.customer, 'item_code': item.item_code})
			if not customer_bin:
				customer_bin = frappe.new_doc('Customer Bin')
				customer_bin.customer = self.customer
				customer_bin.item_code = item.item_code
				customer_bin.available_qty = 0
				customer_bin.save(ignore_permissions = True)
				continue
		
	def on_submit(self):
		self.make_customer_bin()