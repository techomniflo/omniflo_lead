# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
import base64
import json
from frappe.model.document import Document

class SpotlightIssue(Document):
	pass

@frappe.whitelist(allow_guest=True)
def create_spotlight_issue(**kwargs):
	kwargs=frappe._dict(kwargs)
	kwargs=json.loads(json.dumps(kwargs))
	doc=frappe.new_doc("Spotlight Issue")
	doc.is_open=1
	if "brand" in kwargs:
		doc.brand=kwargs['brand']
	if "url" in kwargs:
		doc.url=kwargs["url"]
	if "configuration" in kwargs:
		doc.configuration=kwargs['configuration']
	if "issue" in kwargs:
		doc.issue=kwargs['issue']
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	if "image" in kwargs:
		png_file_name = doc.name + '_spotlight_issue' + frappe.generate_hash(length=20)
		png_file_name = '{}.webp'.format(png_file_name)
		file_doc = frappe.new_doc('File')
		file_doc.file_name = png_file_name
		file_doc.attached_to_doctype="Spotlight Issue"
		file_doc.attached_to_name=doc.name
		file_doc.attached_to_field="image_url"
		file_doc.content=base64.b64decode(kwargs['image'])
		file_doc.save(ignore_permissions=True)
		frappe.db.commit()
		doc.image_url=file_doc.file_url
		doc.save(ignore_permissions=True)
		frappe.delete_doc('File', file_doc.name)
		return