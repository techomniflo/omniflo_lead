# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
import base64
import json
from frappe.model.document import Document

class OmniverseIssue(Document):
	pass

@frappe.whitelist(allow_guest=True)
def create_omniverse_issue(**kwargs):
	kwargs=frappe._dict(kwargs)
	kwargs=json.loads(json.dumps(kwargs))
	doc=frappe.new_doc("Omniverse Issue")
	doc.is_open=1
	if "brand" in kwargs:
		doc.brand=kwargs['brand']
	if "url" in kwargs:
		doc.url=kwargs["url"]
	if "configuration" in kwargs:
		doc.configuration=kwargs['configuration']
	if "issue" in kwargs:
		doc.issue=kwargs['issue']
	if "requested_by" in kwargs:
		doc.requested_by=kwargs['requested_by']
	if "email" in kwargs:
		doc.email=kwargs['email']
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	if "image" in kwargs:
		png_file_name = doc.name + '_omniverse_issue' + frappe.generate_hash(length=20)
		png_file_name = '{}.webp'.format(png_file_name)
		file_doc = frappe.new_doc('File')
		file_doc.file_name = png_file_name
		file_doc.attached_to_doctype="Omniverse Issue"
		file_doc.attached_to_name=doc.name
		file_doc.attached_to_field="image"
		file_doc.content=base64.b64decode(kwargs["image"])
		file_doc.save(ignore_permissions=True)
		frappe.db.commit()
		doc.image=file_doc.file_url
		doc.save(ignore_permissions=True)
		frappe.delete_doc('File', file_doc.name)
		return