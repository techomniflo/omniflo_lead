import frappe
import json

#gives stores data with status and address of it.
@frappe.whitelist()
def stores_list_data():
    stores_list = frappe.db.sql("""select c.customer_name as 'Customer Name', max(vi.creation) as 'Latest Visit log',vi.status, concat(a.address_line1," ",a.address_line2) as address,a.city,a.state,a.country,a.pincode from `tabVisit Log` as vi left join `tabCustomer` as c on vi.customer=c.name left join `tabAddress` as a on a.name=customer_primary_address where customer is not null and customer!="" and c.customer_group!="Brand Platform" group by customer;""",as_dict=True)
    return stores_list

@frappe.whitelist()
def stores_data_with_status():
    store_list=frappe.db.sql("""select c.name as name_id,c.customer_name,c.customer_details as customer_link,c.territory,c.customer_status as status,concat(a.address_line1," ",a.address_line2) as address,a.city,a.state,a.country,a.pincode,(select al.latitude from `tabAudit Log` as al where al.customer=c.name and al.latitude is not null order by posting_date desc limit 1 ) as latitude,(select al.longitude from `tabAudit Log` as al where al.customer=c.name and al.longitude is not null order by posting_date desc limit 1 ) as longitude from `tabCustomer` as c left join `tabDynamic Link` as dl on dl.link_name=c.name join `tabAddress` as a on a.name=dl.parent where dl.link_doctype='Customer' and dl.parenttype='Address' and c.customer_status="Live" and a.is_primary_address=1 and c.name in (select s.customer from `tabSales Invoice` as s where s.docstatus=1 and s.company='Omnipresent Services') and c.name not in (select cp.customer from `tabCustomer Profile` as cp )""",as_dict=True)
    return store_list

@frappe.whitelist()
def stores_gmv_with_first_billing_date():
    return_value=frappe.db.sql("""select meta.customer,meta.Billing_Date,meta.Bill_Amount-meta.Store_Available_Qty_Amount as GMV_Sales,(select sum(-1*pp.grand_total) from `tabPlacement Promotion` as pp where pp.customer=meta.customer and pp.discount_type='Display Discount') as rent from (select 
    si.customer, 
    (
        select 
        min(kk.posting_date) 
        from 
        `tabSales Invoice` as kk 
        where 
        si.customer = kk.customer
    ) as Billing_Date, 
    (
        sum(sii.qty)
    ) as Bill_Qty, 
    (
        select 
        sum(available_qty) 
        from 
        `tabCustomer Bin` as cb 
        join `tabItem` as ii on cb.item_code = ii.item_code 
        where 
        cb.customer = si.customer
    ) as Store_qty, 
    (
        sum(sii.qty * i.mrp)
    ) as Bill_Amount, 
    (
        select 
        sum(available_qty * mrp)
        from 
        `tabCustomer Bin` as cb 
        join `tabItem` as ii on cb.item_code = ii.item_code 
        where
        cb.customer = si.customer
    ) as Store_Available_Qty_Amount 
    from 
    `tabSales Invoice` as si 
    join `tabSales Invoice Item` as sii on si.name = sii.parent 
    join `tabItem` as i on i.item_code = sii.item_code 
    where 
    si.company = "Omnipresent Services" 
    and si.status != 'Cancelled' 
    and si.status != "Draft" 
    group by 
    si.customer 
    order by 
    si.customer) as meta
""",as_dict=True)
    return return_value

@frappe.whitelist()
def item_list():
    rv=frappe.db.sql("""select i.item_code,i.item_name,i.brand,i.mrp from `tabItem` as i where i.name!='Platform Services' and i.name!='test item' and i.brand is not null;""",as_dict=True)
    return rv

@frappe.whitelist()
def customer_list():
    rv=frappe.db.sql("""select c.name,c.customer_name from `tabCustomer` as c where c.name in (select si.customer from `tabSales Invoice` as si where si.customer=c.name and si.company='Omnipresent Services') and c.customer_status!='Closed';""")
    return rv

@frappe.whitelist()
def sales_data():
    return frappe.db.sql(""" select dws.date,dws.customer,(dws.qty*i.mrp) as gmv,i.brand,i.item_name,i.item_code from `tabDay Wise Sales` as dws join `tabItem` as i on i.item_code=dws.item_code """,as_dict=True)