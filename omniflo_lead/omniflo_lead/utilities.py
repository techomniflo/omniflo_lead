
import os
from pyqrcode import create as qrcreate

import frappe
from frappe.model.document import Document
from frappe.utils import get_url

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

def get_doctype_redirection_link(doctype):
	setting = frappe.get_single('Omniflo Setting')
	for qr_code in setting.qr_codes:
		if qr_code.local_doctype == doctype:
			return qr_code.redirection_link
	return None

def qrcode_as_png(doctype, docname):
	'''Save temporary Qrcode to server.'''
	folder = create_barcode_folder()
	qr_code_url = get_doctype_redirection_link(doctype)
	if not qr_code_url:
		return
	
	qr_code_url = qr_code_url + docname
	png_file_name = docname + '_qr_code' + frappe.generate_hash(length=20)
	png_file_name = '{}.png'.format(png_file_name)
	_file = frappe.get_doc({
		"doctype": "File",
		"file_name": png_file_name,
		"attached_to_doctype": doctype,
		"attached_to_name": docname,
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

def disable_s3_backup():
	doc=frappe.get_doc('S3 Backup Settings','S3 Backup Settings')
	doc.enabled=0
	doc.save()
	frappe.db.commit()

def disable_backup_day_wise_sales():
	backup_settings_doc=frappe.get_doc("Omniflo Setting","Omniflo Setting")
	backup_settings_doc.enable_backup_day_wise_sales=0
	backup_settings_doc.save()
	frappe.db.commit()
