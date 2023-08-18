# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class Reconciliation(Document):
	def validate(self):
		for item in self.items:
			if item.quantity==None:
				frappe.throw(
						_("Row {0}: No quantity is filled , Please fill the qty").format(_(item.idx)), title=_("Warning")
					)
			bin_list=frappe.get_list('Bin',filters={"item_code":item.item_code,"warehouse":self.default_warehouse},fields='*')
			if not len(bin_list):
				frappe.throw(_("Row {0}: {1}({2}) is not received yet please remove the row ").format(_(item.idx),_(item.item_code),_(item.item_name)),title=_("Warning"))

	@frappe.whitelist()
	def fetch_brands_item(self,brand):
		values={"brand":brand,"warehouse":self.default_warehouse}
		data=frappe.db.sql("""select i.item_code,i.item_name,b.actual_qty as current_quantity,b.stock_uom  as uom from `tabItem` as i join `tabBin` as b on i.item_code=b.item_code where i.brand=%(brand)s and b.warehouse=%(warehouse)s and i.disabled=0""",values=values,as_dict=True)
		for i in data:
			self.append('items',{
				"item_code":i.item_code,
				"item_name":i.item_name,
				"uom":i.uom,
				"quantity":0,
				"current_quantity":i.current_quantity
			})


	def before_save(self):
		for item in self.items:
				item.difference=item.quantity-item.current_quantity
	
	
	@frappe.whitelist()
	def fetch_items(self):
		# bin_items = frappe.get_all('Bin', filters = {'warehouse' : self.default_warehouse}, fields =['name'])
		bin_items=frappe.db.sql("""select b.name from `tabBin` as b join `tabItem` as i on b.item_code=i.item_code where b.warehouse=%(warehouse)s order by i.brand""",values={'warehouse':self.default_warehouse},as_dict=True)
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
@frappe.whitelist()
def get_current_qty(item_code,warehouse):
	item_actual_qty=frappe.db.sql(""" select b.actual_qty as current_qty from `tabBin` as b where b.item_code=%(item_code)s and b.warehouse=%(warehouse)s """,values={'warehouse':warehouse,'item_code':item_code},as_list=True)
	try:
		return item_actual_qty[0][0]
	except IndexError as e:
		frappe.throw(_("{0} is not Received yet .<br> Kindly remove row.").format(_(item_code)),title=(_("Warning")))