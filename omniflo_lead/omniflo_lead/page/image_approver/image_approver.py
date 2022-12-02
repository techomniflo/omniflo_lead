import frappe
import json

@frappe.whitelist()
def get_details():
    detils_of_image=frappe.db.sql("""select ald.name,al.customer,(ald.item_code)as picture_type,ald.parent,ald.modified_by,(`ald`.`status`)as my_status,ald.image,(DATE_FORMAT(ald.creation,'%d-%m-%y %r')) as date_and_time ,u.full_name from `tabAudit Log Details` as ald join `tabAudit Log` as al on ald.parent = al.name join `tabUser` as u on ald.modified_by=u.email where ald.image is not null and Date(ald.creation) > Date('2022-05-05') and (ald.status="" or ald.status='Hold') and ald.item_code='Shelf' order by ald.creation desc;""",as_dict=True)
    for image in detils_of_image:
        values={'name':image['parent']}
        brand_names=frappe.db.sql(""" select i.brand,(select if((sum(current_available_qty)>0),1,0) from `tabAudit Log` as AL join `tabAudit Log Items` as ALD on ALD.parent=AL.name join `tabItem` as I on I.item_code=ALD.item_code where AL.name=al.name and i.brand=I.brand) as is_present from `tabAudit Log` as al join `tabAudit Log Items` as ald on ald.parent=al.name join `tabItem` as i on i.item_code=ald.item_code where al.name=%(name)s group by i.brand order by is_present desc """,values=values,as_list=True)
        image['brand1']=brand_names[:len(brand_names)//2]
        image['brand2']=brand_names[len(brand_names)//2:]
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
    
