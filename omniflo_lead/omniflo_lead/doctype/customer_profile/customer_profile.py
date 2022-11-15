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
	if "type" in kwargs:
		customer_profile.type=kwargs["type"]
	if "store_timings" in kwargs:
		customer_profile.store_timings=kwargs["store_timings"]
	if "daily_footfall" in kwargs:
		customer_profile.daily_footfall=kwargs["daily_footfall"]
	if "in_society" in kwargs:
		customer_profile.in_society=kwargs["in_society"]
	if "delivery" in kwargs:
		customer_profile.delivery=kwargs["delivery"]
	if "landmarks" in kwargs:
		customer_profile.landmarks=kwargs["landmarks"]
	if "area" in kwargs:
		customer_profile.area=kwargs["area"]
	if "number_of_aisles_inside_the_store" in kwargs:
		customer_profile.number_of_aisles_inside_the_store=kwargs["number_of_aisles_inside_the_store"]
	if "number_of_floors" in kwargs:
		customer_profile.number_of_floors=kwargs["number_of_floors"]
	if "average_order_value" in kwargs:
		customer_profile.average_order_value=kwargs["average_order_value"]
	if "brand_present" in kwargs:
		customer_profile.brand_present=kwargs["brand_present"]
	if "locality_area" in kwargs:
		customer_profile.locality_area=kwargs["locality_area"]
	customer_profile.save(ignore_permissions = True)
	frappe.db.commit()
	return customer_profile

@frappe.whitelist(allow_guest=True)
def customer_data():
	return frappe.db.sql("""select * from `tabCustomer Profile` as cp""",as_dict=True)
	