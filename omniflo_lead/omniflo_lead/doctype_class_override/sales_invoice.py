from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.model.document import Document
from frappe import _
from frappe.utils import add_days, cint, formatdate, get_datetime, getdate
import frappe


class CustomSalesInvoice(SalesInvoice):
	def check_sales_order_on_hold_or_close(self, ref_fieldname):
		for d in self.get("items"):
			if d.get(ref_fieldname):
				status = frappe.db.get_value("Sales Order", d.get(ref_fieldname), "status")
				if status in ("Closed", "On Hold") and not self.is_return:
					frappe.throw(_("Sales Order {0} is {1}").format(d.get(ref_fieldname), status))
	def update_reserved_qty(self):
		so_map = {}
		for d in self.get("items"):
			if d.so_detail:
				if self.doctype == "Delivery Note" and d.against_sales_order:
					so_map.setdefault(d.against_sales_order, []).append(d.so_detail)
				elif self.doctype == "Sales Invoice" and d.sales_order and self.update_stock:
					so_map.setdefault(d.sales_order, []).append(d.so_detail)

		for so, so_item_rows in so_map.items():
			if so and so_item_rows:
				sales_order = frappe.get_doc("Sales Order", so)

				if (sales_order.status == "Closed" and not self.is_return) or sales_order.status in ["Cancelled"]:
					frappe.throw(
						_("{0} {1} is cancelled or closed").format(_("Sales Order"), so), frappe.InvalidStatusError
					)

				sales_order.update_reserved_qty(so_item_rows)
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
