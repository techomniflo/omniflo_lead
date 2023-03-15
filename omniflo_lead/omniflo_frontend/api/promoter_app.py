import frappe
import json

@frappe.whitelist(allow_guest=True)
def create_promoter_log(**kwargs):
	kwargs=frappe._dict(kwargs)
	kwargs=json.loads(json.dumps(kwargs))
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
	return

@frappe.whitelist(allow_guest=True)
def create_promoter_sales_capture(**kwargs):
	kwargs=frappe._dict(kwargs)
	kwargs=json.loads(json.dumps(kwargs))
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

