import frappe
import json
from omniflo_lead.omniflo_frontend.api.promoter_app import upload_file

@frappe.whitelist()
def get_audit_item():
    """ This function is used to get items dict for audit """
    try:
        values={"customer":frappe.request.args["customer"],"item_group":frappe.request.args["item_group"]}
    except:
        frappe.local.response['http_status_code'] = 404
        return "some fields are missing"
    return_value = frappe.db.sql(""" 
                    select 
                        meta.item_code,
                        meta.item_name,
                        meta.brand,
                        ip.image_url, 
                        (meta.billed_qty - meta.sell_qty) as 'expect_qty' 
                        from 
                        (
                            select 
                            sii.item_code, 
                            i.item_name, 
                            si.customer, 
                            i.brand, 
                            sum(sii.qty * sii.conversion_factor) as billed_qty, 
                            (
                                select 
                                if(
                                    sum(dws.qty) is null, 
                                    0, 
                                    sum(dws.qty)
                                ) 
                                from 
                                `tabDay Wise Sales` as dws 
                                where 
                                dws.item_code = sii.item_code 
                                and si.customer = dws.customer
                            ) as sell_qty 
                            from 
                            `tabSales Invoice` as si 
                            join `tabSales Invoice Item` as sii on si.name = sii.parent 
                            join `tabItem` as i on i.item_code = sii.item_code 
                            where 
                            si.docstatus = 1 
                            and si.customer = %(customer)s
                            and i.item_group = %(item_group)s 
                            group by 
                            si.customer, 
                            sii.item_code
                        ) as meta 
                        left join `tabItem Profile` as ip on meta.item_code = ip.item_code 
                        where 
                        meta.billed_qty > 0 
                        and meta.brand not in ('Sample', 'Tester')
                        """,values=values,as_dict=True)
    return sorted(return_value, key=lambda d: (d['expect_qty']==0,d['brand'],d['item_name']))

def update_audit_images(doc,images):
    for count,i in enumerate(images):
        try:
            url=upload_file(doc,field_name="details",content=i["base64"],image_format=i["image_format"])
            child_doc=frappe.get_doc('Audit Log Details',doc.details[count].name)
            child_doc.db_set('image', url, update_modified=False,commit=True)
        except:
            pass

    

@frappe.whitelist(allow_guest=True)
def post_audit_log():
    kwargs = json.loads(frappe.request.data)
    try:
        customer=kwargs['customer']
        item_group=kwargs['item_group']
        items=kwargs['items']
    except:
        frappe.local.response['http_status_code'] = 404
        return "some field are missing"
    images=[]
    for i in kwargs["images"]:
        images.append({'item_code':i['type']})

    doc = frappe.get_doc(
			{
				"doctype": "Audit Log",
                "customer": customer,
                "item_group": item_group,
                "items":items,
                "details":images,
                "latitude": kwargs['latitude'] if "latitude" in kwargs else "",
                "longitude":kwargs['longitude'] if "longitude" in kwargs else ""
			}
		).save(ignore_permissions=True)
    doc.submit()
    if "images" in kwargs:
        frappe.enqueue(update_audit_images,doc=doc,images=kwargs["images"])
    frappe.local.response['http_status_code'] = 201
    return doc
