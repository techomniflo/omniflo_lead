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
    return_value = frappe.db.sql(""" select meta.item_code,i.item_name,i.sub_brand,i.brand,cb.available_qty,ip.image_url,i.mrp from 
                                            ( select tpii.item_code,tpi.customer,null as expected_qty from `tabThird Party Invoicing` as tpi join `tabThird Party Invoicing Item` as tpii on tpi.name=tpii.parent where tpi.docstatus=1 and tpi.customer=%(customer)s

                                                 union

                                            select item_code,customer,billed_qty - sales_qty as expected_qty  from (select sii.item_code,si.customer,sum(sii.qty*sii.conversion_factor) as billed_qty,(select sum(qty) from `tabDay Wise Sales` as dws where dws.customer=si.customer and sii.item_code=dws.item_code ) as sales_qty from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.customer=%(customer)s and si.docstatus=1 group by sii.item_code) as base_si where base_si.billed_qty>0) as meta 
                                 join `tabItem` as i on meta.item_code=i.item_code join `tabCustomer Bin` as cb on cb.item_code=i.item_code and cb.customer=meta.customer left join `tabItem Profile` as ip on ip.item_code=i.item_code where i.item_group=%(item_group)s order by i.brand,i.sub_brand,cb.available_qty desc """,values=values,as_dict=True)
    return return_value

def _update_audit_image(doc,image):
        audit=frappe.get_doc('Audit Log',doc)
        url=upload_file(doc=audit,field_name="details",content=image["base64"],image_format=image["image_format"])
        audit.append('details',{'item_code':image['type'],'image':url})
        audit.save(ignore_permissions=True)

@frappe.whitelist(methods=("POST",))
def update_audit_image():
    kwargs = json.loads(frappe.request.data)
    try:
        doc,image=kwargs['doc'],kwargs['image']
    except:
        frappe.local.response['http_status_code'] = 404
        return "some field are missing"
    frappe.enqueue(_update_audit_image,doc=doc,image=kwargs["image"])
    frappe.local.response['http_status_code'] = 201
    

@frappe.whitelist(methods=("POST",))
def post_audit_log():
    kwargs = json.loads(frappe.request.data)
    try:
        customer=kwargs['customer']
        item_group=kwargs['item_group']
        items=kwargs['items']
    except:
        frappe.local.response['http_status_code'] = 404
        return "some field are missing"

    for x in items:
        if x["in_category_qty"]==None:
            x["current_available_qty"]=x["asset_available_qty"]
        else:
            x["current_available_qty"]=x["asset_available_qty"]+x["in_category_qty"]
    doc = frappe.get_doc(
			{
				"doctype": "Audit Log",
                "customer": customer,
                "item_group": item_group,
                "items":items,
                "latitude": kwargs['latitude'] if "latitude" in kwargs else "",
                "longitude":kwargs['longitude'] if "longitude" in kwargs else "",
                "facing":kwargs["facing"] if "facing" in kwargs else 0
			}
		).save(ignore_permissions=True)
    doc.submit()
    frappe.local.response['http_status_code'] = 201
    return doc

@frappe.whitelist(allow_guest=True)
def pending_audits_list(user):
    """ This API provides a list of stores and the number of days since the last audit. """
    return frappe.db.sql(""" select al.customer,DATEDIFF(curdate(),date(al.posting_date)) days from `tabAudit Log`  as al join (select AL.customer,max(posting_date) as posting_date from `tabAudit Log` as AL where AL.docstatus=1 group by AL.customer) as meta on meta.customer=al.customer and meta.posting_date=al.posting_date join `tabCustomer` as c on c.name=al.customer where c.customer_status='Live' and al.docstatus=1 and al.owner=%(owner)s order by days desc """,values={"owner":user},as_dict=True)

@frappe.whitelist(allow_guest=True)
def stores_audited_today(user):
    """ This API provides a list of stores that were audited today. """
    return frappe.db.sql(""" select count(*) as count,al.customer from  `tabAudit Log` as al where al.docstatus=1 and date(al.posting_date)=curdate() and al.owner=%(owner)s group by al.customer """,values={'owner':user},as_dict=True)
