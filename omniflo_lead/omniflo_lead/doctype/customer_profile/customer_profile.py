# Copyright (c) 2021, Omniflo and contributors
# For license information, please see license.txt

import frappe
import json
import copy
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue

from omniflo_lead.omniflo_lead.utilities import qrcode_as_png

class CustomerProfile(Document):
	pass

@frappe.whitelist(allow_guest=True)
def create_customer(**kwargs):

	kwargs=frappe._dict(kwargs)
	kwargs=json.loads(json.dumps(kwargs))
	values={'customer':kwargs["customer"]}
	customer_profile_doc = frappe.db.sql("""select name from `tabCustomer Profile` where customer=%(customer)s """,values=values,as_dict=True)
	if customer_profile_doc:
		customer_profile=frappe.get_doc('Customer Profile',customer_profile_doc[0]["name"])
	else:
		customer=frappe.db.get_value('Customer',{"name":kwargs["customer"]})
		if not customer:
			return f"Not Found {kwargs['customer']}"
		customer_profile=frappe.new_doc("Customer Profile")
		customer_profile.customer=kwargs["customer"]

	if "name" in kwargs:
		customer_profile.name1=kwargs["name"]
	if "address" in kwargs:
		customer_profile.address=kwargs["address"]
	if "sub_type" in kwargs:
		customer_profile.sub_type=kwargs["sub_type"]
	if "link" in kwargs:
		customer_profile.link=kwargs["link"]
	if "image_url" in kwargs:
		customer_profile.image_url=kwargs["image_url"]
	if "latitude" in kwargs:
		customer_profile.latitude=float(kwargs["latitude"])
	if "longitude" in kwargs:
		customer_profile.longitude=float(kwargs["longitude"])
	if "persqprice" in kwargs:
		customer_profile.persqprice=float(kwargs["persqprice"])
	if "rating" in kwargs:
		customer_profile.rating=float(kwargs["rating"])
	if "review_count"in kwargs:
		customer_profile.review_count=float(kwargs["review_count"])
	if "territory" in kwargs:
		customer_profile.territory=kwargs["territory"]
	customer_profile.save(ignore_permissions = True)
	frappe.db.commit()
	return customer_profile
	