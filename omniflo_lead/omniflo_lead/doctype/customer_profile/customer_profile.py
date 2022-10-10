# Copyright (c) 2021, Omniflo and contributors
# For license information, please see license.txt

import frappe
import json
import copy
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue

from omniflo_lead.omniflo_lead.utilities import qrcode_as_png

class CustomerProfile(Document):
	pass
