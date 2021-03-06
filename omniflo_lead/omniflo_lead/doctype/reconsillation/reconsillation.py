# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Reconsillation(Document):

	def before_save(self):
		for item in self.items:
			item.difference=item.quantity-item.current_quantity
	
	
	@frappe.whitelist()
	def fetch_items(self):
		bin_items = frappe.get_all('Bin', filters = {'warehouse' : self.default_warehouse}, fields =['name'])
		current_items = []
		if self.get('items'):
			current_items = [item.item_code for item in self.get('items')]
		for item in bin_items:
			Bin = frappe.get_doc('Bin', item['name'])
			if Bin.item_code in current_items:
				continue

			item_doc = frappe.get_doc('Item', Bin.item_code)
			self.append('items',
						{'item_code' : Bin.item_code , 
						'item_name' : item_doc.item_name,
						'uom':Bin.stock_uom,
						'current_quantity': Bin.actual_qty })
