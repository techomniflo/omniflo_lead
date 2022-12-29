import frappe

@frappe.whitelist(allow_guest=True)
def get_live_customer():
    return frappe.db.sql("""select c.name as customer,c.customer_name from `tabCustomer` as c where c.customer_status='Live' and c.name not in ( select si.customer from `tabSales Invoice` as si where si.company="Omniway Technologies Pvt Ltd" and si.customer=c.name) order by c.name;""",as_dict=True)


@frappe.whitelist(allow_guest=True)
def return_planogram():
    values={"name":frappe.request.args["planogram_id"]}
    return frappe.db.sql(""" select pi.row,pi.column,pi.brand,pi.item_name,pi.qty from `tabPlanogram Items` as pi where pi.parent=%(name)s order by pi.row,pi.column""",values=values,as_dict=True)

@frappe.whitelist(allow_guest=True)
def find_asset():
    values={"customer":frappe.request.args["customer"]}
    return frappe.db.sql("""select p.name as planogram_id,p.shelf_code as asset_type from `tabPlanogram` as p where p.disabled=0 and p.customer=%(customer)s """,values=values,as_dict=True)