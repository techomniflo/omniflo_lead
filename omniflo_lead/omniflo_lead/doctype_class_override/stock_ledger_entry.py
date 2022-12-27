from erpnext.stock.doctype.stock_ledger_entry.stock_ledger_entry import StockLedgerEntry
from frappe.model.document import Document
import frappe

class CustomStockLedgerEntry(StockLedgerEntry):
	def validate_batch(self):
		if self.batch_no and self.voucher_type != "Stock Entry":
			if (self.voucher_type in ["Purchase Receipt", "Purchase Invoice"] and self.actual_qty < 0) or (
				self.voucher_type in ["Delivery Note", "Sales Invoice"] and self.actual_qty > 0
			):
				return
			if self.voucher_type not in ["Purchase Receipt","Stock Reconciliation","Stock Entry"]:
				expiry_date = frappe.db.get_value("Batch", self.batch_no, "expiry_date")
				if expiry_date:
					if getdate(self.posting_date) > getdate(expiry_date):
						frappe.throw(_("Batch {0} of Item {1} has expired.").format(self.batch_no, self.item_code))
