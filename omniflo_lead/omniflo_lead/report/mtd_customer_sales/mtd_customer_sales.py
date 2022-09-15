# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
import datetime
from omniflo_lead.omniflo_lead.report.overall_brand_sales.overall_brand_sales import Date_wise_sale


def execute(filters=None):
	columns =["mm-yy","MTD Sales","GMV Sales","Billing Date","Agent Name"]
	return columns ,mtd_sales()
 
def mtd_sales():
	sales=Date_wise_sale()
	sales.sort(key=lambda x: (datetime.datetime.strptime(x[0], "%d-%m-%y")),reverse=True)
	today=datetime.date.today()
	curr_month=today.strftime("%d-%m-%y")[3:]
	customer_curr_month_sale={}
	for sale in sales:
		if curr_month==sale[0][3:]:
			if sale[1] not in customer_curr_month_sale:
				customer_curr_month_sale[sale[1]]=int(sale[6])
			else:
				customer_curr_month_sale[sale[1]]+=int(sale[6])
		else:
			break
	
	customer_details=frappe.db.sql("""select meta.customer_name,meta.Bill_Amount-meta.Store_Available_Qty_Amount as GMV_Sales,meta.Billing_Date,meta.manager_name from (select 
    si.customer_name,
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
    ) as Store_Available_Qty_Amount,
    (select c.manager_name from `tabCustomer` as c where c.name=si.customer) as manager_name
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
    si.customer) as meta""",as_list=True)
	return_value=[]
	for i in customer_details:
		if i[0] in customer_curr_month_sale:
			return_value.append([i[0],customer_curr_month_sale[0],i[1],i[2],i[3]])
	return return_value
	
