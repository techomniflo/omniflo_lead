from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.model.document import Document
from frappe import _
from frappe.utils import add_days, cint, formatdate, get_datetime, getdate
import frappe

class CustomSalesInvoice(SalesInvoice):
	@frappe.whitelist()
	def remove_stock_out_qty(self):
		if not self.set_warehouse:
			return
		for item in self.items:
			try:
				bin=frappe.db.sql(""" select b.actual_qty from `tabBin` as b where b.warehouse=%(warehouse)s and b.item_code=%(item_code)s """,values={'warehouse':self.set_warehouse,'item_code':item.item_code})
				bin_qty=bin[0][0]
				if bin_qty < 1:
					self.items.remove(item)
				if bin_qty < item.qty:
					item.qty=bin_qty
			except:
				pass
		for index, row in enumerate(self.items):
			row.idx = index+1
		self.run_method("set_missing_values")
		self.run_method("calculate_taxes_and_totals")
		return 

