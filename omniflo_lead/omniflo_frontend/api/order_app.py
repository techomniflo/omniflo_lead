import json
from datetime import datetime
import frappe
from frappe.utils import add_days, cint, formatdate, get_datetime, getdate

@frappe.whitelist()
def get_item_details():
    try:
        values={'customer':frappe.request.args["customer"],'item_group':frappe.request.args["item_group"],'warehouse':frappe.request.args["warehouse"]}
    except:
        frappe.local.response['http_status_code'] = 400
        return "please pass all the required parameter. "
    get_items=frappe.db.sql("""select i.item_code,i.item_name,i.brand,ip.item_url,sug.planned_qty,sug.actual_qty,sug.sell,sug.billed from `tabItem` as i 
                        join `tabBrand` as b on b.name=i.brand 
                        left join `tabItem Profile` as ip on ip.item_code=i.item_code 
                        left join (select i.item_code,i.item_name,i.brand,pi.qty as planned_qty,b.actual_qty,(select if (sum(dws.qty)>0,sum(dws.qty),0) from `tabDay Wise Sales` as dws where dws.customer=p.customer and dws.item_code=pi.item_code) as sell,(select if (sum(sii.qty*sii.conversion_factor),sum(sii.qty*sii.conversion_factor),0) from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.customer=p.customer and si.docstatus=1 and sii.item_code=pi.item_code) as billed from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent join `tabItem` as i on i.item_code=pi.item_code join `tabBin` as b on b.item_code=i.item_code where p.disabled=0 and p.customer=%(customer)s and i.item_group=%(item_group)s and b.warehouse=%(warehouse)s ) as sug on sug.item_code=i.item_code
                            where b.disabled=0 and i.item_group=%(item_group)s and i.disabled=0  """,values=values,as_dict=True)
    for item in get_items:
        if item['billed'] and item['sell']:
            current_qty=item['billed']-item['sell']
            item['current_qty']=current_qty
            suggested_qty=item['planned_qty']-current_qty
            if item['actual_qty'] < suggested_qty:
                suggested_qty=item['actual_qty'] 
            if suggested_qty>0 :
                item['suggested_qty']=suggested_qty
        item.pop('sell')
        item.pop('billed')
        item.pop('planned_qty')
        item.pop('actual_qty')
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
    return doc




