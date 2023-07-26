import json
from datetime import datetime
import frappe
from frappe.utils import add_days, cint, formatdate, get_datetime, getdate, random_string, now

@frappe.whitelist()
def upolad_image_in_sales_order(doc,image_array):
    for image in image_array:
        file_name=random_string(8)
        file = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": file_name+"."+image['image_format'],
                    "attached_to_doctype": doc.doctype,
                    "attached_to_name": doc.name,
                    "folder": "Home/Attachments",
                    "is_private": 1,
                    "content": image['base64'],
                    "decode": 1,
                }
            ).save(ignore_permissions=True)
        return

@frappe.whitelist()
def get_item_details():
    try:
        values={'customer':frappe.request.args["customer"],'item_group':frappe.request.args["item_group"],'warehouse':frappe.request.args["warehouse"]}
    except:
        frappe.local.response['http_status_code'] = 400
        return "please pass all the required parameter. "
    get_items=frappe.db.sql(""" select i.item_code,i.item_name,i.brand,i.mrp,ip.image_url,sug.planned_qty,sug.sell,sug.billed,bin.actual_qty as warehouse_qty,i.sub_brand from `tabItem` as i 
                        join `tabBrand` as b on b.name=i.brand 
                        left join `tabItem Profile` as ip on ip.item_code=i.item_code
                        left join `tabBin` as bin on bin.item_code=i.item_code and bin.warehouse=%(warehouse)s 
                        left join (select i.item_code,i.item_name,i.brand,pi.qty as planned_qty,(select if (sum(dws.qty)>0,sum(dws.qty),0) from `tabDay Wise Sales` as dws where dws.customer=p.customer and dws.item_code=pi.item_code) as sell,(select if (sum(sii.qty*sii.conversion_factor),sum(sii.qty*sii.conversion_factor),0) from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.customer=p.customer and si.docstatus=1 and sii.item_code=pi.item_code) as billed from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent join `tabItem` as i on i.item_code=pi.item_code  where p.disabled=0 and p.customer=%(customer)s and i.item_group=%(item_group)s  ) as sug on sug.item_code=i.item_code
                            where b.disabled=0 and i.item_group=%(item_group)s and i.disabled=0  """,values=values,as_dict=True)
    for item in get_items:
        if item['billed'] and item['sell']:
            current_qty=item['billed']-item['sell']
            suggested_qty=item['planned_qty']-current_qty
            if item['warehouse_qty'] < suggested_qty:
                suggested_qty=item['warehouse_qty'] 
            if suggested_qty>0 :
                item['suggested_qty']=suggested_qty
        item.pop('sell')
        item.pop('billed')
        item.pop('planned_qty')
    return get_items


@frappe.whitelist(methods=("POST",))
def create_sales_order(**kwargs):
    args = json.loads(frappe.request.data)
    try:
        customer=args["customer"]
        warehouse=args["warehouse"]
        items=args["items"]
        customer_doc=frappe.get_doc('Customer',args["customer"])
    except KeyError:
        frappe.local.response['http_status_code'] = 400
        return "Some argument's are missing. "
    except frappe.DoesNotExistError:
        frappe.clear_messages()
        frappe.local.response['http_status_code'] = 400
        return "Customer is not valid."

    try:
        delivery_date=datetime.strptime(args['delivery_date'],"%d-%m-%Y")
    except:
        delivery_date=add_days(getdate(),1)

    if customer_doc.default_price_list:
        selling_price_list=customer_doc.default_price_list
    else:
        selling_price_list='25%'
       
    doc = frappe.new_doc('Sales Order')
    doc.customer=customer
    doc.set_warehouse=warehouse
    doc.company='Omnipresent Services'
    doc.delivery_date=delivery_date
    doc.order_type='Sales'
    doc.currency='INR'
    doc.selling_price_list=selling_price_list
    for item in items:
        doc.append('items',{'item_code' : item['item_code'], 
						'item_name' : item['item_name'],
						'qty':item['qty'],
						'delivery_date':delivery_date
						})
    doc.run_method("set_missing_values")
    doc.run_method("calculate_taxes_and_totals")
    doc.save()
    doc.submit()
    frappe.enqueue(upolad_image_in_sales_order,doc=doc,image_array=args['images'])
    return doc

@frappe.whitelist(allow_guest=True)
def get_sales_orders(user):
    """ This API provides a list of sales orders created by a user, limited to a length of 20. """
    return frappe.db.sql("""  select so.name,so.creation,so.transaction_date ,so.customer_name, so.delivery_date ,so.set_warehouse, so.customer, so.selling_price_list,so.status,so.set_warehouse,so.total_taxes_and_charges,so.base_total,so.base_rounded_total from `tabSales Order` as so where so.owner=%(owner)s and so.naming_series='SAL-ORD-.YYYY.-' order by name desc limit 20  """,values={'owner':user},as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_sales_order_items_details(doc_name):
    """ This API provides the items for a specific sales order, which is provided by the user. """
    return frappe.db.sql("""  select sii.item_code,sii.item_name,i.mrp,i.brand,i.sub_brand,sii.rate,sii.qty*sii.conversion_factor as qty,sii.qty*sii.rate*sii.conversion_factor as amount,ip.image_url from `tabSales Order Item` as sii join `tabItem`as i on i.item_code=sii.item_code left join `tabItem Profile` as ip on ip.item_code=i.item_code where sii.parent=%(name)s  """,values={'name':doc_name},as_dict=True)

@frappe.whitelist()
def cancel_sales_order(doc_name):
    """ This api is used to cancel sales order """
    
    try:
        doc=frappe.get_doc('Sales Order',doc_name)
        doc.cancel()
        frappe.db.commit()
        return 'Successful'
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        return e







