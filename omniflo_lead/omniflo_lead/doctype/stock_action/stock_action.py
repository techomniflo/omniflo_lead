# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.stock_ledger import NegativeStockError, get_previous_sle
from frappe import _
from frappe.utils import (
	flt,
	format_time,
	formatdate,
)

class StockAction(Document):
	def on_cancel(self):
		if self.reason_type in ["Damage","Expiry"]:
			self.cancel_stock_transfer()
		

	def on_submit(self):
		if self.reason_type in ["Damage","Expiry"]:
			stock_entry=self.make_stock_transfer()
			frappe.db.sql(""" update `tabStock Action` set stock_entry=%(stock_entry)s where name=%(name)s """,values={"name":self.name,"stock_entry":stock_entry})
			frappe.db.commit()
	def validate(self):
		# if user amend or duplicate then it doesnot contain stock entry value
		if self.docstatus==0:
			self.stock_entry=""
		self.check_actual_qty()
	
	def check_actual_qty(self):
		for d in self.get("items"):
			previous_sle = get_previous_sle(
					{
						"item_code": d.item_code,
						"warehouse": self.from_warehouse or self.to_warehouse,
						"posting_date": self.posting_date,
						"posting_time": self.posting_time,
					}
				)
			# get actual stock at source warehouse
			actual_qty = previous_sle.get("qty_after_transaction") or 0

			if (
				self.docstatus == 1
				and self.from_warehouse
				and actual_qty < d.transfer_qty
			):
				frappe.throw(
					_(
						"Row {0}: Quantity not available for {4} in warehouse {1} at posting time of the entry ({2} {3})"
					).format(
						d.idx,
						frappe.bold(self.from_warehouse),
						formatdate(self.posting_date),
						format_time(self.posting_time),
						frappe.bold(d.item_code),
					)
					+ "<br><br>"
					+ _("Available quantity is {0}, you need {1}").format(
						frappe.bold(flt(actual_qty)), frappe.bold(d.qty)
					),
					NegativeStockError,
					title=_("Insufficient Stock"),
				)




	def cancel_stock_transfer(self):
		doc=frappe.get_doc('Stock Entry',self.stock_entry)
		doc.cancel()
	def make_stock_transfer(self):
		doc=frappe.new_doc("Stock Entry")
		doc.company=self.company
		doc.posting_date=self.posting_date
		doc.posting_time=self.posting_time
		doc.stock_entry_type="Material Transfer"
		doc.from_warehouse=self.from_warehouse
		doc.to_warehouse=self.to_warehouse
		for i in self.items:
			doc.append("items",{"item_code":i.item_code,"s_warehouse":self.from_warehouse,"t_warehouse":self.to_warehouse,"qty":i.qty,"uom":i.uom})
		doc.save(ignore_permissions=True)
		doc.submit()
		return doc.name

