import erpnext
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
def on_submit(doc, event):
	doclist=make_purchase_invoice(doc.name)
	doclist.bill_no=doc.supplier_invoice_no
	doclist.bill_date=doc.supplier_invoice_date
	doclist.save()
	doclist.submit()