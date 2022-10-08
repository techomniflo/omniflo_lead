import frappe
import requests
import json
import os
from pyqrcode import create as qrcreate
from omniflo_lead.omniflo_lead.utilities import create_barcode_folder
from omniflo_lead.omniflo_lead.doctype_events.file import file_upload_to_s3
# from frappe.utils import get_url
import png
import base64


def on_submit(doc, event):
    for item in doc.items:
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
    
    create_qr_code(doc)
    file_doc = frappe.db.get_value('File', {'attached_to_doctype': 'Sales Invoice', 'attached_to_name': doc.name})
    if file_doc:
        file_doc=frappe.get_doc("File",file_doc)
        doc.qr_code_url=file_doc.file_url


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

def create_qr_code(self):
    if self.status!='Return' and self.company=='Omnipresent Services':
        try:
            qrcode_as_png(customer=self.customer,invoiceNo=self.name,amount=self.rounded_total,gstin=self.customer_gstin)
        except:
            pass

def qrcode_as_png(customer,invoiceNo,amount,email=None,contact=None,gstin=None,notes=None):
    doctype='Sales Invoice'
    docname='qr_code_url'

    qr_code_url = createQR(customer, invoiceNo, amount, email, contact, gstin, notes)


    if not qr_code_url:
        return

    url = qrcreate(qr_code_url)
    png_file_name = docname + '_qr_code' + frappe.generate_hash(length=20)
    png_file_name = '{}.png'.format(png_file_name)
    _file = frappe.get_doc({
		"doctype": "File",
		"file_name": png_file_name,
		"attached_to_doctype": doctype,
		"attached_to_name": invoiceNo,
        "attached_to_field":docname,
		"content": base64.b64decode(url.png_as_base64_str(scale=3, module_color=(0, 0, 0, 255), background=(255, 255, 255, 255), quiet_zone=4))
    })
    _file.save()
    
    frappe.db.commit()
    file_upload_to_s3(doc=_file,method=None)

    return



def createQR(name, invoiceNo, amount, email=None, contact=None, gstin=None, notes=None):
    amount = amount * 100  #convert paise to rs
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic cnpwX2xpdmVfZFN5dVFVeUxYVzJtU1g6UjRDM0kzbVNNNmlmTWJBVG9tc3BYQkJt'
        }
    def createCustomer(name, email="", contact="",gstin="",notes={}):
        url = "https://api.razorpay.com/v1/customers"
        
        data = {
                "name": name,
                "email": email,
                "contact": contact,
                "fail_existing": "0",
                "notes": notes
            }
        if gstin:
            data["gstin"] = gstin
        payload = json.dumps(data)
        response = requests.request("POST", url, headers=headers, data=payload)
        return (response.text)
    customer = json.loads(createCustomer(name, email, contact=contact, gstin=gstin,notes={}))
    url = "https://api.razorpay.com/v1/payments/qr_codes"
    data = {
        "type": "upi_qr",
        "name": invoiceNo,
        "usage": "multiple_use",
        "fixed_amount": False,
        "payment_amount": amount,
        "description": "For "+name+" against "+invoiceNo,
        "customer_id": customer["id"],
        "notes": {
            "invoice": invoiceNo,
            "amount": amount,
            "customer": name
        }
    }
    payload = json.dumps(data)
    response = requests.request("POST", url, headers=headers, data=payload)
    plink = json.loads(response.text)
    # print("plink is", plink)
    ic = plink["image_content"]
    return ic
    