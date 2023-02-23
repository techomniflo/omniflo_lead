import frappe
import json

def get_context(context):
	# do your magic here
	pass

@frappe.whitelist(allow_guest=True)
def fetch_billed_details(customer):
    values={"customer":customer}
    data=frappe.db.sql("""select i.brand,i.item_name,i.item_code,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code where i.brand not in ('Sample','Tester') and si.docstatus=1 and si.customer=%(customer)s and 0<(select sum(SII.qty) from `tabSales Invoice` as SI join `tabSales Invoice Item` as SII on SI.name=SII.parent where SI.docstatus=1 and SI.company=si.company and SI.customer=si.customer and SII.item_code=sii.item_code) group by i.brand,i.item_name,i.item_code,i.mrp""",values=values,as_dict=True)
    brand_details={}
    for i in data:
        if i['brand'] not in brand_details:
            brand_details[i['brand']]=[(i['item_name'],"mrp:- "+str(i['mrp']),i['item_code'])]
        else:
            brand_details[i['brand']].append((i['item_name'],"mrp:- "+str(i['mrp']),i['item_code']))
    return brand_details
