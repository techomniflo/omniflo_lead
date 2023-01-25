# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.model.document import Document

class CustomerOrder(WebsiteGenerator):
	def validate(self):
		self.route=self.name
		self.published=1
	def on_submit(self):
		self.route=""
		self.published=0

	@frappe.whitelist()
	def fetch_items(self):
		if self.item_group==None:
			item_group=""
		else:
			item_group=f"""and item_group='{self.item_group}'"""
		db_query=f""" select i.item_code,i.item_name,i.brand,pi.qty as planned_qty,b.actual_qty,(select if (sum(dws.qty)>0,sum(dws.qty),0) from `tabDay Wise Sales` as dws where dws.customer=p.customer and dws.item_code=pi.item_code) as sell,(select if (sum(sii.qty*sii.conversion_factor),sum(sii.qty*sii.conversion_factor),0) from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.customer=p.customer and si.docstatus=1 and sii.item_code=pi.item_code) as billed from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent join `tabItem` as i on i.item_code=pi.item_code join `tabBin` as b on b.item_code=i.item_code where p.disabled=0 and p.customer='{self.customer}' {item_group} and b.warehouse='{self.warehouse}' order by i.item_group,i.brand,i.item_name """
		items_dict=frappe.db.sql(db_query,as_dict=True)
		for item in items_dict:
			item_to_deploy=item['planned_qty']-(item['billed']-item['sell'])
			if item_to_deploy<1 or item['actual_qty']<1:
				continue
			if item['actual_qty']-item_to_deploy<0 and item['actual_qty']>0:
				item_to_deploy=item['actual_qty']
			self.append('items',
						{'item_code' : item['item_code'], 
						'item_name' : item['item_name'],
						'brand': item['brand'],
						'qty':item_to_deploy
						})
@frappe.whitelist()
def is_brand_in_planogram(brand,customer):
	check_brand=frappe.db.sql("""select distinct i.brand from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent join `tabItem` as i on i.item_code=pi.item_code where p.disabled=0 and p.customer=%(customer)s and i.brand=%(brand)s group by i.brand""",values={'customer':customer,'brand':brand},as_dict=True)
	if len(check_brand)>0:
		return True
	return False