# Copyright (c) 2021, Omniflo and contributors
# For license information, please see license.txt

import frappe

from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue

from omniflo_lead.omniflo_lead.utilities import qrcode_as_png

class CustomerProfile(Document):
	def before_save(self):
		self.create_qr_code()
	
	def create_qr_code(self):
		if self.qr_code:
			return
		try:
			file_url = qrcode_as_png('Customer Profile', self.customer)
			self.qr_code = file_url
		except:
			pass
