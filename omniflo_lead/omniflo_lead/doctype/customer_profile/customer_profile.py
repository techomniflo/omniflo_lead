# Copyright (c) 2021, Omniflo and contributors
# For license information, please see license.txt

import os
import frappe

from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from pyqrcode import create as qrcreate
from frappe.utils import get_url

class CustomerProfile(Document):
	def before_save(self):
		self.create_qr_code()
	
	def create_qr_code(self):
		if self.qr_code:
			return
		try:
			file_url = qrcode_as_png(self.customer)
			self.qr_code = file_url
		except:
			pass

def qrcode_as_png(customer):
	'''Save temporary Qrcode to server.'''
	folder = create_barcode_folder()
	qr_code_url = 'link.omniflo.in/' + customer
	png_file_name = customer + '_qr_code' + frappe.generate_hash(length=20)
	png_file_name = '{}.png'.format(png_file_name)
	_file = frappe.get_doc({
		"doctype": "File",
		"file_name": png_file_name,
		"attached_to_doctype": 'Customer Profile',
		"attached_to_name": customer,
		"folder": folder,
		"content": png_file_name})
	_file.save()
	frappe.db.commit()
	file_url = get_url(_file.file_url)
	file_path = os.path.join(frappe.get_site_path('public', 'files'), _file.file_name)
	url = qrcreate(qr_code_url)
	with open(file_path, 'wb') as png_file:
		url.png(png_file, scale=8)
	return file_url

def create_barcode_folder():
	'''Get Barcodes folder.'''
	folder_name = 'Barcodes'
	folder = frappe.db.exists('File', {'file_name': folder_name})
	if folder:
		return folder
	folder = frappe.get_doc({
			'doctype': 'File',
			'file_name': folder_name,
			'is_folder':1,
			'folder': 'Home'
		})
	folder.insert(ignore_permissions=True)
	return folder.name