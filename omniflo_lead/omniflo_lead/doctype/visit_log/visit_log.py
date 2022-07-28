# Copyright (c) 2021, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VisitLog(Document):
	def on_submit(self):
		# adding status to customer
		customer=frappe.get_doc('Customer',self.customer)
		if customer.customer_status!=self.status:
			customer.customer_status=self.status
			customer.save(ignore_permissions=True)


		#adding latitude and longitude to customer
		try:
			customer_doc = frappe.get_doc('Customer', self.customer)
			if not customer_doc.latitude:
				customer_doc.latitude = self.latitude
			if not customer_doc.longitude:
				customer_doc.longitude = self.longitude
			customer_doc.save()
		except:
			pass
