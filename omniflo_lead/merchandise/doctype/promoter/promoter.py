# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Promoter(Document):
	def after_insert(self):
		doc=frappe.get_doc('Promoter',self.name)
		doc.full_name=doc.first_name+" "+doc.last_name
		doc.save(ignore_permissions = True)		
