import frappe

@frappe.whitelist()
def get_audit_item():
    """ This function is used to get items dict for audit """
    try:
        values={"customer":frappe.request.args["customer"],"item_group":frappe.request.args["item_group"]}
    except:
        frappe.local.response['http_status_code'] = 404
        return "some fields are missing"
    return_value = frappe.db.sql(""" 
                    select 
                        meta.item_code,
                        meta.item_name,
                        meta.brand,
                        ip.image_url, 
                        (meta.billed_qty - meta.sell_qty) as 'expect_qty' 
                        from 
                        (
                            select 
                            sii.item_code, 
                            i.item_name, 
                            si.customer, 
                            i.brand, 
                            sum(sii.qty * sii.conversion_factor) as billed_qty, 
                            (
                                select 
                                if(
                                    sum(dws.qty) is null, 
                                    0, 
                                    sum(dws.qty)
                                ) 
                                from 
                                `tabDay Wise Sales` as dws 
                                where 
                                dws.item_code = sii.item_code 
                                and si.customer = dws.customer
                            ) as sell_qty 
                            from 
                            `tabSales Invoice` as si 
                            join `tabSales Invoice Item` as sii on si.name = sii.parent 
                            join `tabItem` as i on i.item_code = sii.item_code 
                            where 
                            si.docstatus = 1 
                            and si.customer = %(customer)s
                            and i.item_group = %(item_group)s 
                            group by 
                            si.customer, 
                            sii.item_code
                        ) as meta 
                        left join `tabItem Profile` as ip on meta.item_code = ip.item_code 
                        where 
                        meta.billed_qty > 0 
                        and meta.brand not in ('Sample', 'Tester')
                        """,values=values,as_dict=True)
    return sorted(return_value, key=lambda d: (d['expect_qty']==0,d['brand'],d['item_name']))