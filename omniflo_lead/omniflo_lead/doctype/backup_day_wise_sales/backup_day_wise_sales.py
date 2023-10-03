# Copyright (c) 2023, Omniflo and contributors
# For license information, please see license.txt

import frappe
import boto3
import csv
from io import StringIO
from datetime import datetime
from frappe.model.document import Document

class BackupDayWiseSales(Document):
	pass

def backup_day_wise_sales():

	s3_settings_doc = frappe.get_doc(
			'S3 File Attachment',
			'S3 File Attachment',
		)
	s3 = boto3.resource('s3',aws_access_key_id=s3_settings_doc.get_password('aws_key'),aws_secret_access_key=s3_settings_doc.get_password('aws_secret'))

	data=frappe.db.sql("""select dws.date,dws.customer,dws.item_code,dws.qty,dws.sale_from,dws.age,dws.gender from `tabDay Wise Sales` as dws""",as_dict=True)
	s3_folder='Day_Wise_Sales_backup'
	s3_file_name=datetime.now().strftime("%d%m%Y_%H%M%S")
	file_path=f'{s3_folder}/{s3_file_name}.csv'

	csv_data = StringIO()
	csv_writer = csv.DictWriter(csv_data, fieldnames=data[0].keys())
	csv_writer.writeheader()
	csv_writer.writerows(data)
	csv_content = csv_data.getvalue()
	x=s3.Object('engine-omniflo',file_path).put(Body=csv_content)
	doc = frappe.get_doc(
			{
				"doctype": "Backup Day Wise Sales",
				"url":"https://files.omniflo.in/"+file_path
			}
		).save(ignore_permissions=True)



