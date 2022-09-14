import frappe
import json

#gives stores data with status and address of it.
@frappe.whitelist()
def stores_list_data():
    stores_list = frappe.db.sql("""select c.customer_name as 'Customer Name', max(vi.creation) as 'Latest Visit log',vi.status, concat(a.address_line1," ",a.address_line2) as address,a.city,a.state,a.country,a.pincode from `tabVisit Log` as vi left join `tabCustomer` as c on vi.customer=c.name left join `tabAddress` as a on a.name=customer_primary_address where customer is not null and customer!="" and c.customer_group!="Brand Platform" group by customer;""",as_dict=True)
    return stores_list

@frappe.whitelist()
def stores_data_with_status():
    store_list=frappe.db.sql("""select `tabCustomer`.customer_name,AL.status,(concat (A.address_line1," ",A.address_line2)) as address,A.city,A.state,A.pincode,`tabCustomer`.longitude,`tabCustomer`.latitude from `tabVisit Log` as AL left join `tabCustomer` on `tabCustomer`.name=AL.customer left join `tabDynamic Link` as dl on dl.link_name=`tabCustomer`.name left join `tabAddress` as A on A.name=dl.parent  where AL.modified in (select max(modified) from `tabVisit Log` where AL.customer=customer) and `tabCustomer`.customer_name is not null group by `tabCustomer`.customer_name;""",as_dict=True)
    return store_list

@frappe.whitelist()
def stores_gmv_with_first_billing_date():
    return_value=frappe.db.sql("""select meta.customer,meta.Billing_Date,meta.Bill_Amount-meta.Store_Available_Qty_Amount as GMV_Sales from (select 
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
