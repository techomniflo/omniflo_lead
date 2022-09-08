# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Promoter(Document):
	def on_save(self):
		self.full_name=self.first_name+" "+self.last_name
		
