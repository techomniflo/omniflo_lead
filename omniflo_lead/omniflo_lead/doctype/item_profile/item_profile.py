# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class ItemProfile(Document):
	pass

@frappe.whitelist(allow_guest=True)
def create_item_profile(**kwargs):
	kwargs=frappe._dict(kwargs)
	kwargs=json.loads(json.dumps(kwargs))
	values={'item_code':kwargs["item_code"]}
	item_profile_doc = frappe.db.sql("""select name from `tabItem Profile` where item_code=%(item_code)s """,values=values,as_dict=True)
	if item_profile_doc:
		item_profile=frappe.get_doc('Item Profile',item_profile_doc[0]["name"])
	else:
		item=frappe.db.get_value('Item',{"name":kwargs["item_code"]})
		if not item:
			return f"Not Found {kwargs['item_code']}"
		item_profile=frappe.new_doc("Item Profile")
		item_profile.item_code=kwargs["item_code"]

	if "scrapped_name" in kwargs:
		item_profile.scrapped_name=kwargs["scrapped_name"]
	if "item_url" in kwargs:
		item_profile.item_url=kwargs["item_url"]
	if "image_url" in kwargs:
		item_profile.image_url=kwargs["image_url"]
	if "price" in kwargs:
		item_profile.price=float(kwargs["price"])
	if "uom" in kwargs:
		item_profile.uom=kwargs["uom"]
	if "uom_qty" in kwargs:
		item_profile.uom_qty=kwargs["uom_qty"]
	
	item_profile.save(ignore_permissions = True)
	frappe.db.commit()
	return item_profile
