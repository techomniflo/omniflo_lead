# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from omniflo_lead.omniflo_lead.api.frappe_api import calculate_gmv

class DayWiseSales(Document):
	pass

@frappe.whitelist(allow_guest=True)
def day_sales():
	previous_doc=frappe.get_list('Day Wise Sales')
	for i in previous_doc:
		frappe.delete_doc('Day Wise Sales', i['name'])
	gmv_data=calculate_gmv()
	for i in gmv_data:
		doc=frappe.new_doc('Day Wise Sales')
		doc.date=i[0]
		doc.customer=i[1]
		doc.qty=i[2]
		doc.item_code=i[3]
		doc.brand=i[4]
		doc.item_name=i[6]
		doc.gmv=i[7]
		doc.sale_from=i[5]
		doc.save(ignore_permission=True)


	
