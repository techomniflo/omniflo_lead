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
from erpnext.controllers.accounts_controller import get_taxes_and_charges
import json


class StockAction(Document):
	def on_cancel(self):
		if self.reason_type in ["Damage","Expiry","Sampling"]:
			self.cancel_stock_transfer()
		if self.reason_type in ["Sampling","Dispose"]:
			doc=frappe.get_doc("Purchase Invoice",self.purchase_invoice)
			doc.cancel()
		

	def on_submit(self):
		if self.reason_type in ["Damage","Expiry"]:
			stock_entry=self.make_stock_transfer()
			frappe.db.sql(""" update `tabStock Action` set stock_entry=%(stock_entry)s where name=%(name)s """,values={"name":self.name,"stock_entry":stock_entry})
			frappe.db.commit()

		if self.reason_type == "Sampling":
			purchase_invoice=self.make_purchase_return()
			stock_entry=self.receive_sample_item()
			frappe.db.sql(""" update `tabStock Action` set stock_entry=%(stock_entry)s,purchase_invoice=%(purchase_invoice)s where name=%(name)s """,values={"name":self.name,"stock_entry":stock_entry,"purchase_invoice":purchase_invoice})
			frappe.db.commit()

		if self.reason_type == "Dispose":
			purchase_invoice=self.make_purchase_return()
			frappe.db.sql(""" update `tabStock Action` set purchase_invoice=%(purchase_invoice)s where name=%(name)s """,values={"name":self.name,"purchase_invoice":purchase_invoice})
			frappe.db.commit()

	def validate(self):
		# if user amend or duplicate then it doesnot contain stock entry value
		if self.docstatus==0:
			self.stock_entry=""
		if self.de_from=="Supplier":
			self.check_pr_item()
		if self.reason_type in ("Sampling","Dispose"):
			self.validate_supplier_for_sampling()
		self.check_actual_qty()
	
	def check_pr_item(self):
		if (self.docstatus == 1 and self.purchase_receipt):
			pr=frappe.get_doc("Purchase Receipt",self.purchase_receipt)
			# It checks for warehouse
			if pr.set_warehouse!=self.from_warehouse:
				frappe.throw(_("In Purchase Receipt accepted warehouse is {0} and in Stock Action warehouse is {1} both are different.").format(frappe.bold(pr.set_warehouse),frappe.bold(self.from_warehouse)),title=_("Warehouse difference error"))
			
			items=pr.as_dict()["items"]
			pr_items_dict={}
			for item in items:
				if item["item_code"] not in pr_items_dict:
					pr_items_dict[item["item_code"]]=item["stock_qty"]
				else:
					pr_items_dict[item["item_code"]]+=item["stock_qty"]

			for item in self.items:
				item_code=item.item_code
				item_name=item.item_name
				#checking if item and qty is correct or not
				if item_code not in pr_items_dict:
					frappe.throw(_("Row {2}:Item {0} ({1}) not in Purchase Receipt but It is in Stock Action").format(frappe.bold(item_code),item_name,item.idx),title=_("Item Mismatch"))
				elif item.transfer_qty>pr_items_dict[item_code]:
					frappe.throw(_("Row {2}:Qty of Item {0} ({1}) is greater than qty in Purchase Receipt").format(frappe.bold(item_code),item_name,item.idx),title=_("Qty Mismatch"))

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
				and (self.from_warehouse or self.to_warehouse)
				and actual_qty < d.transfer_qty
			):
				frappe.throw(
					_(
						"Row {0}: Quantity not available for {4} in warehouse {1} at posting time of the entry ({2} {3})"
					).format(
						d.idx,
						frappe.bold(self.from_warehouse or self.to_warehouse),
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

	def validate_supplier_for_sampling(self):
		for item in self.items:
			item_details=frappe.db.sql(""" select sum(pii.qty) as qty from `tabPurchase Invoice` as pi join `tabPurchase Invoice Item` as pii on pi.name=pii.parent where pi.docstatus=1 and pi.company=%(company)s and pii.item_code=%(item_code)s and pi.supplier=%(supplier)s  """,values={"supplier":self.supplier,"item_code":item.item_code,"company":self.company},as_dict=True)
			if item_details[0]['qty']==None:
				frappe.throw(f"item {item.item_code} : {item.item_name} is not recieved from Supplier: {self.supplier} <br> please double check supplier ")

	def make_purchase_return(self):
		doc=frappe.new_doc("Purchase Invoice")
		doc.company=self.company
		doc.supplier=self.supplier
		doc.posting_date=self.posting_date
		doc.posting_time=self.posting_time
		doc.is_return=1
		doc.update_stock=1
		if self.reason_type in ("Damage","Expiry"):
			doc.set_warehouse=self.from_warehouse
		else:
			doc.set_warehouse=self.to_warehouse

		for item in self.items:
			doc.append('items',{'item_code':item.item_code,'qty':-1*item.qty,'rate':0,'uom':item.uom})

		
		doc.run_method("set_missing_values")
		set_taxes(doc)
		doc.run_method("calculate_taxes_and_totals")
		doc.run_method("onload")
		doc.save(ignore_permissions=True)
		doc.submit()
		return doc.name
	
	def set_taxes(self,doc):
		taxes=get_taxes_and_charges(master_doctype='Purchase Taxes and Charges Template',master_name=doc.taxes_and_charges)
		for tax in taxes:
			doc.append("taxes",tax)

	def receive_sample_item(self):
		doc=frappe.new_doc("Stock Entry")
		doc.company=self.company
		doc.posting_date=self.posting_date
		doc.posting_time=self.posting_time
		doc.stock_entry_type="Material Receipt"
		doc.to_warehouse=self.to_warehouse
		
		for item in self.items:
		
			sample_item=frappe.get_value("Sample Item Mapper",item.item_code,"sample_item_code")
			if not sample_item:
				sample_item=self.create_sample_item(item.item_code)

			doc.append("items",{"item_code":sample_item,"s_warehouse":self.from_warehouse,"qty":item.qty,"uom":item.uom,"allow_zero_valuation_rate":1})
		
		doc.save(ignore_permissions=True)
		doc.submit()
		self.stock_entry=doc.name
		return doc.name

	def create_sample_item(self,item_code):
		item_doc=frappe.get_doc("Item",item_code)
		item_code_no=frappe.db.sql(""" select max(cast(substring(i.item_code,14,17) as INTEGER ) )  from `tabItem` as i; """,as_list=True)[0][0]+1
		sample_item=frappe.copy_doc(item_doc)
		sample_item.item_code='OMNI-ITM-SAM-'+str(item_code_no)
		sample_item.item_name='Sample -'+item_doc.item_name
		sample_item.barcodes=[]
		sample_item.item_group='Sample'
		sample_item.last_purchase_rate=0
		sample_item.save(ignore_permissions=True)

		mapper_doc=frappe.new_doc("Sample Item Mapper")
		mapper_doc.item_code=item_code
		mapper_doc.sample_item_code=sample_item.item_code
		mapper_doc.save(ignore_permissions=True)

		
		frappe.clear_cache()
		return sample_item.item_code
	
	@frappe.whitelist()
	def set_previous_gle_queue(self):
		rv=[]
		for item in self.items:
			previous_sle = get_previous_sle(
						{
							"item_code": item.item_code,
							"warehouse": self.to_warehouse or self.from_warehouse,
							"posting_date": self.posting_date,
							"posting_time": self.posting_time,
						}
					)
			previous_stock_queue=previous_sle.get("stock_queue") or []
			frappe.db.sql(""" update `tabStock Action Item` set previous_stock_queue=%(previous_stock_queue)s where name=%(name)s """,values={"name":item.name,"previous_stock_queue":previous_stock_queue})
			frappe.db.commit()

def set_taxes(doc):
		taxes=get_taxes_and_charges(master_doctype='Purchase Taxes and Charges Template',master_name=doc.taxes_and_charges)
		for tax in taxes:
			doc.append("taxes",tax)

		


