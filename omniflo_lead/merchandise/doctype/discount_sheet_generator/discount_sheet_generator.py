# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DiscountSheetGenerator(Document):

	@frappe.whitelist()
	def fetch_items(self,brand_offer):
		values={"customer":self.customer,"brand_offer":brand_offer}
		fetch_data=frappe.db.sql("""
		select
		bo.item_code,bo.item_name,bo.brand,bo.mrp,bo.offer_price,bo.difference,bo.offer_percentage,meta.name
		from 
		`tabBrand Offers Items` as bo 
		inner join (
			select
			si.name,
			i.item_code, 
			i.item_name, 
			i.brand, 
			i.mrp, 
			(
				sum(sii.qty)
			) as Bill_Qty 
			from 
			`tabSales Invoice` as si 
			join `tabSales Invoice Item` as sii on si.name = sii.parent 
			join `tabItem` as i on i.item_code = sii.item_code 
			join `tabCustomer` as c on c.name = si.customer 
			where 
			si.company = "Omnipresent Services" 
			and si.status != 'Cancelled' 
			and si.status != "Draft" 
			and si.customer = %(customer)s 
			group by 
			i.brand, 
			si.customer, 
			i.item_name
		) as meta on meta.item_code = bo.item_code
		where bo.parent=%(brand_offer)s """,values=values,as_dict=True)
		sales_invoices=set()
		for i in fetch_data:
			sales_invoices.add(i.name)
			self.append('items',{
				"item_code":i.item_code,
				"item_name":i.item_name,
				"brand":i.brand,
				"mrp":i.mrp,
				"offer_price":i.offer_price,
				"difference":i.difference,
				"offer_percentage":i.offer_percentage
			})
		if self.invoices:
			for invoices in self.invoices:
				sales_invoices.add(invoices.invoice_name)
		self.invoices={}
		sales_invoices=list(sales_invoices)
		for invoice_name in sales_invoices:
			self.append("invoices",{
				"invoice_name":invoice_name
			})