# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DiscountSheetGenerator(Document):

	@frappe.whitelist()
	def fetch_items(self,brand_offer):
		frappe.msgprint(brand_offer)