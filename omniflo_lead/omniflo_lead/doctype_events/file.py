from __future__ import unicode_literals

import datetime
import os
import random
import re
import string

import boto3

from botocore.client import Config
from botocore.exceptions import ClientError

import frappe



class S3Operations(object):

	def __init__(self):
		"""
		Function to initialise the aws settings from frappe S3 File attachment
		doctype.
		"""
		self.s3_settings_doc = frappe.get_doc(
			'S3 File Attachment',
			'S3 File Attachment',
		)
		if (
			self.s3_settings_doc.aws_key and
			self.s3_settings_doc.aws_secret
		):
			self.S3_CLIENT = boto3.client(
				's3',
				aws_access_key_id=self.s3_settings_doc.get_password('aws_key'),
				aws_secret_access_key=self.s3_settings_doc.get_password('aws_secret'),
				region_name=self.s3_settings_doc.region_name,
				config=Config(signature_version='s3v4')
			)
		else:
			self.S3_CLIENT = boto3.client(
				's3',
				region_name=self.s3_settings_doc.region_name,
				config=Config(signature_version='s3v4')
			)
		self.BUCKET = self.s3_settings_doc.bucket_name
		self.folder_name = self.s3_settings_doc.folder_name

	def strip_special_chars(self, file_name):
		"""
		Strips file charachters which doesnt match the regex.
		"""
		regex = re.compile('[^0-9a-zA-Z._-]')
		file_name = regex.sub('', file_name)
		return file_name

	def key_generator(self, file_name, parent_doctype, parent_name):
		"""
		Generate keys for s3 objects uploaded with file name attached.
		"""
		hook_cmd = frappe.get_hooks().get("s3_key_generator")
		if hook_cmd:
			try:
				k = frappe.get_attr(hook_cmd[0])(
					file_name=file_name,
					parent_doctype=parent_doctype,
					parent_name=parent_name
				)
				if k:
					return k.rstrip('/').lstrip('/')
			except:
				pass

		file_name = file_name.replace(' ', '_')
		file_name = self.strip_special_chars(file_name)
		key = ''.join(
			random.choice(
				string.ascii_uppercase + string.digits) for _ in range(8)
		)

		today = datetime.datetime.now()
		year = today.strftime("%Y")
		month = today.strftime("%m")
		day = today.strftime("%d")

		doc_path = None

		if not doc_path:
			if self.folder_name:
				final_key = self.folder_name + "/" + year + "/" + month + \
					"/" + day + "/" + parent_doctype + "/" + key + "_" + \
					file_name
			else:
				final_key = year + "/" + month + "/" + day + "/" + \
					parent_doctype + "/" + key + "_" + file_name
			return final_key
		else:
			final_key = doc_path + '/' + key + "_" + file_name
			return final_key

	def upload_files_to_s3_with_key(
			self, file_path, file_name, is_private, parent_doctype, parent_name
	):
		"""
		Uploads a new file to S3.
		Strips the file extension to set the content_type in metadata.
		"""
		print('//////', file_name)
		key = self.key_generator(file_name, parent_doctype, parent_name)
		try:
			self.S3_CLIENT.upload_file(
					file_path, self.BUCKET, key
			)

		except boto3.exceptions.S3UploadFailedError:
			frappe.throw(frappe._("File Upload Failed. Please try again."))
		return key

	def delete_from_s3(self, key):
		"""Delete file from s3"""
		self.s3_settings_doc = frappe.get_doc(
			'S3 File Attachment',
			'S3 File Attachment',
		)

		if self.s3_settings_doc.delete_file_from_cloud:
			s3_client = boto3.client(
				's3',
				aws_access_key_id=self.s3_settings_doc.get_password('aws_key'),
				aws_secret_access_key=self.s3_settings_doc.get_password('aws_secret'),
				region_name=self.s3_settings_doc.region_name,
				config=Config(signature_version='s3v4')
			)

			try:
				s3_client.delete_object(
					Bucket=self.s3_settings_doc.bucket_name,
					Key=key
				)
			except ClientError:
				frappe.throw(frappe._("Access denied: Could not delete file"))

	def read_file_from_s3(self, key):
		"""
		Function to read file from a s3 file.
		"""
		return self.S3_CLIENT.get_object(Bucket=self.BUCKET, Key=key)

	def get_url(self, key, file_name=None):
		"""
		Return url.
		:param bucket: s3 bucket name
		:param key: s3 object key
		"""
		if self.s3_settings_doc.signed_url_expiry_time:
			self.signed_url_expiry_time = self.s3_settings_doc.signed_url_expiry_time # noqa
		else:
			self.signed_url_expiry_time = 120
		params = {
				'Bucket': self.BUCKET,
				'Key': key,

		}
		if file_name:
			params['ResponseContentDisposition'] = 'filename={}'.format(file_name)

		url = self.S3_CLIENT.generate_presigned_url(
			'get_object',
			Params=params,
			ExpiresIn=self.signed_url_expiry_time,
		)

		return url


@frappe.whitelist(allow_guest=True)
def file_upload_to_s3(doc, method):
	"""
	check and upload files to s3. the path check and
	"""
	s3_upload = S3Operations()
	path = doc.file_url
	site_path = frappe.utils.get_site_path()
	parent_doctype = str(doc.attached_to_doctype)
	parent_name = str(doc.attached_to_name)
	ignore_s3_upload_for_doctype = frappe.local.conf.get('ignore_s3_upload_for_doctype') or ['Data Import']
	if parent_doctype not in ignore_s3_upload_for_doctype:
		if not doc.is_private:
			file_path = site_path + '/public' + path
		else:
			file_path = site_path + path
		key = s3_upload.upload_files_to_s3_with_key(
			file_path, doc.file_name,
			doc.is_private, parent_doctype,
			parent_name
		)

		file_url = '{}/{}/{}'.format(
				s3_upload.S3_CLIENT.meta.endpoint_url,
				s3_upload.BUCKET,
				key
		)
		os.remove(file_path)
		frappe.db.sql("""UPDATE `tabFile` SET file_url=%s, folder=%s,
			old_parent=%s, content_hash=%s WHERE name=%s""", (
			file_url, 'Home/Attachments', 'Home/Attachments', key, doc.name))
		
		doc.file_url = file_url
		if parent_doctype=='None':
			frappe.db.commit()
			return
		if parent_doctype and frappe.get_meta(parent_doctype).get('image_field'):
			frappe.db.set_value(parent_doctype, parent_name, frappe.get_meta(parent_doctype).get('image_field'), file_url)

		frappe.db.commit()

