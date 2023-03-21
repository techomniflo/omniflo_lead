import frappe
import json
import copy
from frappe.utils import random_string

def upload_file(doc,field_name,content,image_format):
	file_name=random_string(8)

	file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": file_name+"."+image_format,
				"attached_to_doctype": doc.doctype,
				"attached_to_name": doc.name,
				"attached_to_field": field_name,
				"folder": "Home/Attachments",
				"is_private": 1,
				"content": content,
				"decode": 1,
			}
		).save(ignore_permissions=True)
	url=copy.copy(file.file_url)
	file.delete()
	return url

def create_promoter_hygiene(promoter_log,kwargs):
	promoter_hygiene = frappe.get_doc(
			{
				"doctype": "Promoter Hygiene",
				"promoter_log":promoter_log,
				"check_in_category_placement": kwargs["check_in_category_placement"],
				"set_merchandising": kwargs["set_merchandising"],
				"set_offers": kwargs["set_offers"],
				"set_per_planogram": kwargs["set_per_planogram"],
				"clean_products_and_shelf": kwargs["clean_products_and_shelf"],
				"check_uniform_and_id_card": kwargs["check_uniform_and_id_card"],
			}
		).save(ignore_permissions=True)

	if "selfie" in kwargs and len(kwargs["selfie"])>0:
		if len(kwargs["selfie"][0]):
			image_format=kwargs["selfie"][0]["format"]
			selfie_url=upload_file(doc=promoter_hygiene,field_name="selfie",content=kwargs["selfie"][0]["base64"],image_format=image_format)
			promoter_hygiene.db_set('selfie',selfie_url)

	for i in kwargs["capture_all_asset"]:
		image_format=i["format"]
		url=upload_file(promoter_hygiene,"image",i["base64"],image_format)
		promoter_hygiene.append("capture_all_asset",
			{"image":url})
	promoter_hygiene.save(ignore_permissions=True)
	return


@frappe.whitelist(allow_guest=True)
def create_promoter_log(**kwargs):
	kwargs = json.loads(frappe.request.data)
	promoter_log= frappe.new_doc('Promoter Log')
	promoter_doc=frappe.get_doc('Promoter',kwargs['promoter'])
	promoter_log.promoter_name=promoter_doc.full_name
	promoter_log.item_group=promoter_doc.item_group
	promoter_log.promoter=kwargs['promoter']
	promoter_log.is_present=kwargs['is_present']
	if kwargs['is_present']==1:
		promoter_log.customer=kwargs['customer']
		customer=frappe.get_doc('Customer',kwargs['customer'])
		promoter_log.customer_name=customer.customer_name

		promoter_log.latitude=kwargs['latitude']
		promoter_log.longitude=kwargs['longitude']
		promoter_log.event_type=kwargs['event_type']
	else:
		promoter_log.leave_type=kwargs['leave_type']
		promoter_log.duration=kwargs['duration']
		if 'duration' in kwargs:
			promoter_log.reason=kwargs['duration']
	promoter_log.save(ignore_permissions=True)
	if kwargs["is_present"]==1:
		if kwargs["event_type"]=="check in":
			create_promoter_hygiene(promoter_log.name,kwargs)
	return

@frappe.whitelist(allow_guest=True)
def create_promoter_sales_capture(**kwargs):
	kwargs = json.loads(frappe.request.data)
	psc_doc = frappe.new_doc('Promoter Sales Capture')
	psc_doc.customer=kwargs['customer']
	psc_doc.promoter=kwargs['promoter']
	psc_doc.qty=kwargs['qty']
	psc_doc.brand=kwargs['brand']
	psc_doc.item_name=kwargs['item_name']
	psc_doc.item_code=kwargs['item_code']
	if 'age' in kwargs:
		psc_doc.age=kwargs['age']
	if 'gender' in kwargs:
		psc_doc.gender=kwargs['gender']
	if 'in_category' in kwargs:
		psc_doc.in_category=kwargs['in_category']
	psc_doc.save(ignore_permissions=True)
	return

@frappe.whitelist(allow_guest=True)
def get_customer_location():
	values={"customer":frappe.request.args["customer"]}
	return frappe.db.sql("select cp.latitude,cp.longitude from `tabCustomer Profile` as cp where cp.customer=%(customer)s",values=values,as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_items():
	promoter=frappe.get_doc('Promoter',frappe.request.args["promoter"])
	values={"customer":frappe.request.args["customer"],"item_group":promoter.item_group}
	data=frappe.db.sql("""select i.brand,i.item_name,i.item_code,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code where i.brand not in ('Sample','Tester') and i.item_group=%(item_group)s and si.docstatus=1 and si.customer=%(customer)s and 0<(select sum(SII.qty) from `tabSales Invoice` as SI join `tabSales Invoice Item` as SII on SI.name=SII.parent where SI.docstatus=1 and SI.company=si.company and SI.customer=si.customer and SII.item_code=sii.item_code) group by i.brand,i.item_name,i.item_code,i.mrp""",values=values,as_dict=True)
	brand_details={}
	for i in data:
		if i['brand'] not in brand_details:
			brand_details[i['brand']]=[{"item_name":i['item_name'],"mrp":i['mrp'],"item_code":i['item_code']}]
		else:
			brand_details[i['brand']].append({"item_name":i['item_name'],"mrp":i['mrp'],"item_code":i['item_code']})
	return brand_details

@frappe.whitelist(allow_guest=True)
def today_promoters_log():
	values={"promoter":frappe.request.args["promoter"]}
	return frappe.db.sql("""select pl.creation,pl.promoter,pl.customer,pl.event_type,pl.is_present,pl.latitude,pl.longitude from `tabPromoter Log` as pl where pl.promoter=%(promoter)s and date(pl.creation)=curdate() order by pl.creation """,values=values,as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_target():
	values={"promoter":frappe.request.args["promoter"]}
	wtd=frappe.db.sql(""" select date(pl.creation) as date,pl.promoter,pl.customer,pl.item_group,ct.target/day(ct.end_date) as per_day_target,(select sum(i.mrp*psc.qty) from `tabPromoter Sales Capture` as psc join `tabItem` as i on i.item_code=psc.item_code where psc.promoter=pl.promoter and date(psc.creation)=date(pl.creation) ) as gmv from `tabPromoter Log` as pl join `tabCustomer Target` as ct on ct.item_group=pl.item_group and date(pl.creation) between ct.start_date and ct.end_date join `tabCustomer Target Item` as cti on cti.customer=pl.customer and cti.parent=ct.name where is_present=1 and week(curdate())=week(pl.creation) and year(curdate())=year(pl.creation) and pl.promoter=%(promoter)s group by pl.customer,pl.promoter,date(pl.creation) order by date(pl.creation)""",values=values,as_dict=True)
	current_date=frappe.db.sql("""select ct.target/day(ct.end_date) as target,(select sum(i.mrp*psc.qty) from `tabPromoter Sales Capture` as psc join `tabItem` as i on i.item_code=psc.item_code where psc.promoter=pl.promoter and date(psc.creation)=date(pl.creation) ) as gmv from `tabPromoter Log` as pl join `tabCustomer Target` as ct on ct.item_group=pl.item_group and date(pl.creation) between ct.start_date and ct.end_date join `tabCustomer Target Item` as cti on cti.customer=pl.customer and cti.parent=ct.name where is_present=1 and date(pl.creation)=curdate() and pl.promoter=%(promoter)s group by pl.customer,pl.promoter,date(pl.creation) order by date(pl.creation)""",values=values,as_dict=True)
	days=6
	total_wtd_target=0
	total_wtd_gmv=0
	for i in wtd:
		if i["gmv"]==None:
			i["gmv"]=0
		if i["per_day_target"]==None:
			i["per_day_target"]=0
		total_wtd_gmv+=i["gmv"]
		total_wtd_target+=i["per_day_target"]
		days-=1
	if days and len(wtd)>0:
		total_wtd_target+=days*wtd[-1]["per_day_target"]
	if len(current_date)==0:
		return {"week":{"target":total_wtd_target,"gmv":total_wtd_gmv},"today":{"target":0,"gmv":0}}
	return {"week":{"target":total_wtd_target,"gmv":total_wtd_gmv},"today":{"target":current_date[0]["target"] or 0,"gmv":current_date[0]["gmv"] or 0}}
	

