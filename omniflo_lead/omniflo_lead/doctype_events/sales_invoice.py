import frappe
import requests
import json
import os
from erpnext.selling.doctype.sales_order.sales_order import update_status
from pyqrcode import create as qrcreate
from omniflo_lead.omniflo_lead.utilities import create_barcode_folder
from omniflo_lead.omniflo_lead.doctype_events.file import file_upload_to_s3
# from frappe.utils import get_url
import png
import base64

def validate(doc,events):
	if doc.is_return==1:
		unique_sales_invoice_item=dict()
		for item in doc.items:
			if item.sales_invoice_item:
				if item.sales_invoice_item in unique_sales_invoice_item:
					frappe.throw(f"Row {item.idx} and Row {unique_sales_invoice_item[item.sales_invoice_item]} both are referring to same Sales Invoice")
				else:
					unique_sales_invoice_item[item.sales_invoice_item]=item.idx
			check_rate_of_ref_invoice(item.rate,item.sales_invoice_item,item.idx)
			check_balance_to_mark_return(doc,item.sales_invoice_item,item.qty,item.idx)

def check_rate_of_ref_invoice(rate,sales_invoice_item,row):
	sales_invoice_item_doc=frappe.get_doc('Sales Invoice Item',sales_invoice_item)
	if rate!=sales_invoice_item_doc.rate:
		frappe.throw(f"Row {row}: Rate cannot be greater than the rate used in Sales Invoice {sales_invoice_item_doc.parent}")
def check_balance_to_mark_return(doc,sales_invoice_item,qty,row):
	data=frappe.db.sql(""" select sii.qty,(select if(sum(SII.qty),abs(sum(SII.qty)),0) from `tabSales Invoice Item` as SII where SII.sales_invoice_item=sii.name and SII.docstatus=1) as return_item from `tabSales Invoice Item` as sii where sii.name=%(sales_invoice_item)s """,values={"sales_invoice_item":sales_invoice_item},as_dict=True)[0]
	balance_qty=data["qty"]-data["return_item"]

	if abs(qty)>balance_qty:
		frappe.throw(f"Row {row}: Cann't mark return more than {balance_qty} for this row")

def before_cancel(doc,events):
	change_sales_order_status(doc,'Re-Open')

def on_submit(doc, event):
	for item in doc.items:
		if item.brand=='Sample' or item.brand=='Tester' or item.item_group=='Sample':
			continue
		customer_bin = frappe.db.get_value('Customer Bin', {'customer': doc.customer, 'item_code': item.item_code})
		if not customer_bin:
			customer_bin = frappe.new_doc('Customer Bin')
			customer_bin.customer = doc.customer
			customer_bin.item_code = item.item_code
			customer_bin.available_qty = item.stock_qty
			customer_bin.stock_uom = item.stock_uom
			customer_bin.save(ignore_permissions = True)
			continue
		else:
			customer_bin = frappe.get_doc('Customer Bin', customer_bin)
			qty=customer_bin.available_qty
			if qty+item.stock_qty>0:
				customer_bin.available_qty += item.stock_qty
				
			else:
				customer_bin.available_qty=0
			customer_bin.stock_uom = item.stock_uom
			customer_bin.save(ignore_permissions = True)
	change_sales_order_status(doc,'Closed')
	create_discount_ledger(doc)

def create_discount_ledger(doc):
	if doc.company!='Omnipresent Services' or doc.is_return==1:
		return

	taxes=[]
	try:
		margin_percentage=int(doc.selling_price_list[:2])
	except Exception:
		return
	customer_group=doc.customer_group
	for tax in doc.taxes:
		if tax.charge_type=="On Net Total":
			taxes.append(tax.account_head)
	for item in doc.items:
		item_tax_template=item.item_tax_template
		tax_percentage=get_tax_percentage(tax_type=taxes,item_tax_template=item_tax_template)
		discount_percentage=calculate_discount_percentage(customer_group=customer_group,mrp=item.mrp,rate=item.rate,margin_percentage=margin_percentage,tax_percentage=tax_percentage)
		if discount_percentage:
			frappe.get_doc({
				'doctype':'Discount Ledger',
				'item_code':item.item_code,
				'voucher_type':'Sales Invoice',
				'voucher_no':doc.name,
				'voucher_details_no':item.name,
				'posting_date':doc.posting_date,
				'posting_time':doc.posting_time,
				'uom':item.uom,
				'qty':item.qty,
				'is_cancelled':0,
				'mrp':item.mrp,
				'discount_percentage':discount_percentage,
				'company':doc.company
			}).save(ignore_permissions=True)

def on_cancel(doc,event):
	for item in doc.items:
		customer_bin = frappe.db.get_value('Customer Bin', {'customer': doc.customer, 'item_code': item.item_code})
		if not customer_bin:
			pass
		else:
			customer_bin = frappe.get_doc('Customer Bin', customer_bin)
			qty=customer_bin.available_qty
			if qty-item.stock_qty<0:
				customer_bin.available_qty=0
			else:
				customer_bin.available_qty -= item.stock_qty
				customer_bin.stock_uom = item.stock_uom
				customer_bin.save(ignore_permissions = True)
	cancel_discount_ledger(doc)

def cancel_discount_ledger(doc):
	if doc.company!='Omnipresent Services' or doc.is_return==1:
		return
	for item in doc.items:
		discount_ledger_doc_name = frappe.db.get_value('Discount Ledger', {'voucher_type': 'Sales Invoice', 'voucher_no':doc.name,'voucher_details_no':item.name})
		if discount_ledger_doc_name:
			discount_ledger_doc = frappe.get_doc('Discount Ledger', discount_ledger_doc_name)
			discount_ledger_doc.is_cancelled=1
			discount_ledger_doc.save(ignore_permissions=True)	

def change_sales_order_status(doc,status):
	if doc.is_return:
		return
	sales_orders=set()
	for item in doc.items:
		if item.sales_order:
			sales_orders.add(item.sales_order)
	for orders in sales_orders:
		try:
			doc=frappe.get_doc("Sales Order",orders)
			if status=='Closed' and doc.status not in ["Closed","Cancelled","Completed"]:
				update_status(status='Closed',name=orders)
			elif status=='Re-Open' and doc.status in ["Closed"]:
				update_status(status="Draft",name=orders)
		except:
			pass

def calculate_discount_percentage(customer_group,mrp,rate,margin_percentage,tax_percentage):
	if rate==0:
		return 100
	per_sku_amount=rate+(rate*tax_percentage/100)
	if	customer_group=='Margin on Mrp':
		margin=margin_percentage*mrp/100
		discount_amount=(mrp-per_sku_amount)-margin
		discount_percentage=round((discount_amount/mrp)*100)
	elif customer_group=='Margin on Discount':
		add_margin_to_rate=per_sku_amount/(1-(margin_percentage/100))
		if add_margin_to_rate==mrp-(mrp*margin_percentage/100):
			discount_percentage=0
		else:
			discount_percentage=round((1-add_margin_to_rate/mrp )*100)
	else:
		discount_percentage = None
	return discount_percentage
		
def get_tax_percentage(tax_type,item_tax_template:str) -> int:
	if len(tax_type)==1:
		tax_type=tax_type[0]
		sql= f"""select sum(iitd.tax_rate) from `tabItem Tax Template` as iit join `tabItem Tax Template Detail` as iitd on iit.name=iitd.parent where iit.name='{item_tax_template}' and iitd.tax_type = '{tax_type}' """
	else:
		tax_type=tuple(tax_type)
		sql= f"""select sum(iitd.tax_rate) from `tabItem Tax Template` as iit join `tabItem Tax Template Detail` as iitd on iit.name=iitd.parent where iit.name='{item_tax_template}' and iitd.tax_type in {tax_type} """
	total_tax=frappe.db.sql(sql,as_list=True)
	if total_tax:
		return total_tax[0][0]