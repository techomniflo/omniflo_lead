import frappe
import json

@frappe.whitelist()
def get_details(type=""):
    if type!="":
        type=f"""and php.type='{type}'"""
    image_details = frappe.db.sql(""" select php.name as photos_doc_name,php.creation,php.image,php.type,ph.*,pl.customer,pl.promoter,pl.item_group from `tabPromoter Hygiene` as ph join `tabPromoter Hygiene Photos` as php on ph.name=php.parent join `tabPromoter Log` as pl on pl.name=ph.promoter_log where php.type is not null and (php.status is null or php.status='') """+type,as_dict=True)
    return image_details

@frappe.whitelist()
def approve(data,index):
    data = json.loads(data)
    index=int(index)
    doc=frappe.get_doc("Promoter Hygiene Photos",data[index]['photos_doc_name'])
    doc.db_set('status', 'Approve', update_modified=False)

@frappe.whitelist()
def reject(data,index,reason):
    data = json.loads(data)
    index=int(index)
    doc=frappe.get_doc("Promoter Hygiene Photos",data[index]['photos_doc_name'])
    doc.db_set('status', 'Reject', update_modified=False)
    doc.db_set('reason', reason, update_modified=False)