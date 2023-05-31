# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from omniflo_lead.omniflo_lead.doctype.day_wise_sales.day_wise_sales import run_day_sales


class UpdateSales(Document):
	@frappe.whitelist()
	def update_sales_in_background(self):
		frappe.enqueue(run_day_sales)
		return

