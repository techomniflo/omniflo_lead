import frappe
import json

def get_context(context):
	# do your magic here
	pass

@frappe.whitelist()
def fetch_item(brand):
    values={"brand":brand}
    return frappe.db.sql("""select item_name from `tabItem` where brand=%(brand)s""",values=values,as_dict=True)