import frappe

@frappe.whitelist(allow_guest=True)
def get_live_customer():
    return frappe.db.sql("""select c.name as customer,c.customer_name,a.address_line1,a.address_line2,a.city,a.state,a.country,a.pincode from `tabCustomer` as c join `tabDynamic Link` as dl on dl.link_name=c.name join `tabAddress` as a on a.name=dl.parent where c.customer_status='Live' and c.name not in ( select si.customer from `tabSales Invoice` as si where si.company="Omniway Technologies Pvt Ltd" and si.customer=c.name)  and dl.link_doctype='Customer' and dl.parenttype='Address' and a.is_primary_address=1 group by c.name order by c.name;""",as_dict=True)


@frappe.whitelist(allow_guest=True)
def return_planogram():
    values={"name":frappe.request.args["planogram_id"]}
    return frappe.db.sql(""" select pi.row,pi.column,i.brand,i.item_name,pi.qty from `tabPlanogram Items` as pi join `tabItem` as i on pi.item_code=i.item_code where pi.parent=%(name)s order by pi.row,pi.column""",values=values,as_dict=True)

@frappe.whitelist(allow_guest=True)
def find_asset():
    values={"customer":frappe.request.args["customer"]}
    return frappe.db.sql("""select p.name as planogram_id,p.shelf_code as asset_type from `tabPlanogram` as p where p.disabled=0 and p.customer=%(customer)s """,values=values,as_dict=True)

# this function is to find suggested refil qty based on planogram.
@frappe.whitelist()
def get_suggested_items(item_group,warehouse,customer):
	
	suggested_items=[]
	if item_group=='All':
		item_group=""
	else :
		item_group=f"""and item_group='{item_group}'"""
	frappe.msgprint(item_group)
	db_query=f""" select i.item_code,i.item_name,i.brand,pi.qty as planned_qty,b.actual_qty,(select if (sum(dws.qty)>0,sum(dws.qty),0) from `tabDay Wise Sales` as dws where dws.customer=p.customer and dws.item_code=pi.item_code) as sell,(select if (sum(sii.qty*sii.conversion_factor),sum(sii.qty*sii.conversion_factor),0) from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.customer=p.customer and si.docstatus=1 and sii.item_code=pi.item_code) as billed from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent join `tabItem` as i on i.item_code=pi.item_code join `tabBin` as b on b.item_code=i.item_code where p.disabled=0 and p.customer='{customer}' {item_group} and b.warehouse='{warehouse}' order by i.item_group,i.brand,i.item_name """
	items_dict=frappe.db.sql(db_query,as_dict=True)
	for item in items_dict:
		item_to_deploy=item['planned_qty']-(item['billed']-item['sell'])
		if item_to_deploy<1 or item['actual_qty']<1:
			continue
		if item['actual_qty']-item_to_deploy<0 and item['actual_qty']>0:
			item_to_deploy=item['actual_qty']
		suggested_items.append(
					{'item_code' : item['item_code'], 
					'item_name' : item['item_name'],
					'brand': item['brand'],
					'qty':item_to_deploy
					})
	return suggested_items