import frappe
import json

@frappe.whitelist()
def get_details():
    detils_of_image=frappe.db.sql("""select ald.name,al.customer,(ald.item_code)as picture_type,ald.parent,ald.modified_by,(`ald`.`status`)as my_status,ald.image,(DATE_FORMAT(ald.creation,'%d-%m-%y %r')) as date_and_time ,u.full_name from `tabAudit Log Details` as ald join `tabAudit Log` as al on ald.parent = al.name join `tabUser` as u on ald.modified_by=u.email where ald.image is not null and Date(ald.creation) > Date('2022-05-05') and (ald.status="" or ald.status='Hold') and ald.item_code='Shelf' order by ald.creation desc;""",as_dict=True)
    return detils_of_image

@frappe.whitelist()
def approve(data,index):
    data = json.loads(data)
    index=int(index)
    doc=frappe.get_doc("Audit Log Details",data[index]['name'])
    doc.db_set('status', 'Approve', update_modified=False)

@frappe.whitelist()
def reject(data,index,reason):
    data = json.loads(data)
    index=int(index)
    doc=frappe.get_doc("Audit Log Details",data[index]['name'])
    doc.db_set('status', 'Reject', update_modified=False)
    doc.db_set('reason', reason, update_modified=False)



@frappe.whitelist()
def on_hold(data,index):
    data = json.loads(data)
    index=int(index)
    doc=frappe.get_doc("Audit Log Details",data[index]['name'])
    doc.db_set('status', 'Hold', update_modified=False)

# @frappe.whitelist()
# def Pass(data,index):
#     data = json.loads(data)
#     index=int(index)
#     doc=frappe.get_doc("Audit Log Details",data[index]['name'])
#     doc.db_set('status', 'Error', update_modified=False)
    
