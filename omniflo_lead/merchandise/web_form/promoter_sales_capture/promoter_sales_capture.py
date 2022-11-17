import frappe
import json

def get_context(context):
	# do your magic here
	pass

@frappe.whitelist(allow_guest=True)
def fetch_item_name(brand):
    values={"brand":brand}
    return frappe.db.sql("""select item_name from `tabItem` where brand=%(brand)s""",values=values,as_dict=True)

@frappe.whitelist(allow_guest=True)
def fetch_item_code(item_name,brand):
    values={"brand":brand,"item_name":item_name}
    x=frappe.db.sql("""select name from `tabItem` where brand=%(brand)s  and item_name=%(item_name)s """,values=values,as_dict=True)
    return x[0]["name"]
    
