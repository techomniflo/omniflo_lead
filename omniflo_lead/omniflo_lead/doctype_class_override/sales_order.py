from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from frappe.model.document import Document
from frappe import _
from frappe.utils import add_days, cint, formatdate, get_datetime, getdate
import frappe

class CustomSalesOrder(SalesOrder):
	@frappe.whitelist()
	def add_planogram_qty(self,item_group,customer,warehouse):
		if item_group=='All':
			item_group=""
		else :
			item_group=f"""and item_group='{item_group}'"""
		db_query=f""" select i.item_code,i.item_name,i.brand,pi.qty as planned_qty,b.actual_qty,(select if (sum(dws.qty)>0,sum(dws.qty),0) from `tabDay Wise Sales` as dws where dws.customer=p.customer and dws.item_code=pi.item_code) as sell,(select if (sum(sii.qty*sii.conversion_factor),sum(sii.qty*sii.conversion_factor),0) from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.customer=p.customer and si.docstatus=1 and sii.item_code=pi.item_code) as billed from `tabPlanogram` as p join `tabPlanogram Items` as pi on p.name=pi.parent join `tabItem` as i on i.item_code=pi.item_code join `tabBin` as b on b.item_code=i.item_code where p.disabled=0 and p.customer='{customer}' {item_group} and b.warehouse='{warehouse}' order by i.item_group,i.brand,i.item_name """
		items_dict=frappe.db.sql(db_query,as_dict=True)
		for item in items_dict:
			item_to_deploy=item['planned_qty']-(item['billed']-item['sell'])
			if item_to_deploy<1 or item['actual_qty']<1:
				continue
			if item['actual_qty']-item_to_deploy<0 and item['actual_qty']>0:
				item_to_deploy=item['actual_qty']
			self.append('items',{'item_code' : item['item_code'], 
						'item_name' : item['item_name'],
						'qty':item_to_deploy,
						'delivery_date':self.delivery_date
						})

		self.run_method("set_missing_values")
		self.run_method("calculate_taxes_and_totals")
		return 