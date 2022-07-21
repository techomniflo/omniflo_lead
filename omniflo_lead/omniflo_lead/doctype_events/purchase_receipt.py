import erpnext
import frappe
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
def on_submit(doc, event):
	doclist=make_purchase_invoice(doc.name)
	doclist.bill_no=doc.supplier_invoice_no
	doclist.bill_date=doc.supplier_invoice_date
	doclist.save()
	doclist.submit()

	# setting expiry and manufacturing date in batch
	for item in doc.items:
		item_doc=frappe.get_doc('Item',item.item_code)
		if item_doc.has_batch_no:
			shelf_life_in_days=item_doc.shelf_life_in_days
			Batch_details=frappe.get_doc('Batch',item.batch_no)
			Batch_details.expiry_date=item.expiry_date
			Batch_details.manufacturing_date=frappe.utils.add_days(item.expiry_date,-1*shelf_life_in_days)
			Batch_details.save(ignore_permissions = True)