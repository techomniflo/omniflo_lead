# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StoreOrder(Document):
	@frappe.whitelist()
	def fetch_items(self):
		items_dict=frappe.db.sql(""" select i.item_code,i.item_name,i.brand,pi.qty as planned_qty,(select if (sum(dws.qty)>0,sum(dws.qty),0) from `tabDay Wise Sales` as dws where dws.customer=p.customer and dws.item_code=pi.item_code) as sell,(select if (sum(sii.qty*sii.conversion_factor),sum(sii.qty*sii.conversion_factor),0) from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.customer=p.customer and si.docstatus=1 and sii.item_code=pi.item_code) as billed from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent join `tabItem` as i on i.item_code=pi.item_code where p.disabled=0 and p.customer=%(customer)s and i.item_group=%(item_group)s order by i.brand,i.item_name """,values={'customer':self.customer,'item_group':self.item_group},as_dict=True)
		for item in items_dict:
			if item['planned_qty']-(item['billed']-item['sell'])<0:
				continue
			self.append('items',
						{'item_code' : item['item_code'], 
						'item_name' : item['item_name'],
						'brand': item['brand'],
						'qty':item['planned_qty']-(item['billed']-item['sell'])
						})