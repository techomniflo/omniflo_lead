from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.model.document import Document
from frappe import _
from frappe.utils import add_days, cint, formatdate, get_datetime, getdate
import frappe


class CustomSalesInvoice(SalesInvoice):
	@frappe.whitelist()
	def remove_stock_out_qty(self):
		to_remove=[]
		if self.set_warehouse and self.update_stock==0:
			frappe.msgprint(" Please Set Warehouse ")
			return
		for item in self.items:
			try:
				bin=frappe.db.sql(""" select b.actual_qty from `tabBin` as b where b.warehouse=%(warehouse)s and b.item_code=%(item_code)s """,values={'warehouse':self.set_warehouse,'item_code':item.item_code})
				bin_qty=bin[0][0]
				if bin_qty < 1:
					to_remove.append(item.idx)
				elif bin_qty < item.qty :
					item.qty=bin_qty
			except:
				pass

		self.run_method("set_missing_values")
		self.run_method("calculate_taxes_and_totals")
		if self.name[0:3]!='new':
			self.save()
		return to_remove
