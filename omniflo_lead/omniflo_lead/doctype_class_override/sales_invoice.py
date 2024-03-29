from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.model.document import Document
from frappe import _
from erpnext.controllers.sales_and_purchase_return import get_returned_qty_map_for_row
from frappe.utils import flt,add_days, cint, formatdate, get_datetime, getdate
from frappe.model.mapper import map_fields
import frappe
from frappe.utils import cstr


class CustomSalesInvoice(SalesInvoice):

	@frappe.whitelist()
	def create_return(self,source_doc_name,child_name,qty):

		def update_item(source_doc, target_doc, qty,target_parent,source_parent):

			returned_qty_map = qty
			target_doc.qty = -1* qty  #* flt(source_doc.qty - (returned_qty_map.get("qty") or 0))
			target_doc.stock_qty = -1 * qty #* flt(source_doc.stock_qty - (returned_qty_map.get("stock_qty") or 0))

			target_doc.sales_order = source_doc.sales_order
			target_doc.delivery_note = source_doc.delivery_note
			target_doc.so_detail = source_doc.so_detail
			target_doc.dn_detail = source_doc.dn_detail
			target_doc.expense_account = source_doc.expense_account
			target_doc.sales_invoice_item = source_doc.name

			if target_parent.set_warehouse:
				target_doc.warehouse = target_parent.set_warehouse
			else:
				target_doc.warehouse=""

		table_map={'doctype': 'Sales Invoice Item', 'field_map': {'serial_no': 'serial_no', 'batch_no': 'batch_no', 'bom': 'bom'}, 'postprocess': update_item}
		source_d=frappe.get_doc('Sales Invoice Item',child_name)
		source_doc=frappe.get_doc('Sales Invoice',source_doc_name)
		map_child_doc(source_d=source_d,target_parent=self,table_map=table_map,source_parent=source_doc,qty=qty)

	
	@frappe.whitelist()
	def bulk_return(self,arr):
		required_fields=['item_code','qty','uom']
		for count,name in enumerate(arr[0]):
			if name in required_fields :
				required_fields.remove(name)
				if name=='item_code':
					item_code_column=count
				elif name=='qty':
					qty_column=count
				elif name=='uom':
					uom_column=count
			if not required_fields:
				break
		if required_fields:
			rfs=", ".join(required_fields)
			frappe.msgprint(msg=f"<b> Warning </b>: <strong> {rfs} </strong> fields are missing from csv file.",indicator='red',title='warning')
			return
		
		for count,row in enumerate(arr[1:]):
			if row!=['']:
				item_code=row[item_code_column]
				qty=row[qty_column]
				uom=row[uom_column]
				message=self.fifo_qty(item={'item_code':item_code,'qty':int(qty),'uom':uom})
				if message:
					frappe.msgprint(msg=f"CSV Row {count+2}: " + message,indicator='red',title='warning')
			

	@frappe.whitelist()
	def fifo_qty(self,item):
		if not self.customer:
			frappe.msgprint("Please Set Customer")
			return
		remaining_qty=item['qty']

		fifo=frappe.db.sql("""   select si.name,si.posting_date,si.posting_time,TIMESTAMP(si.posting_date,si.posting_time) as posting_date_time,sii.item_code,sii.qty,sii.uom,sii.name as child_name,( select sii.qty-if(abs(sum(SII.qty)),abs(sum(SII.qty)),0) from `tabSales Invoice Item` as SII where SII.sales_invoice_item=sii.name and SII.docstatus=1 ) as balance_qty from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent where si.docstatus=1  and si.company='Omnipresent Services' and si.customer=%(customer)s and sii.item_code=%(item_code)s and si.discount_amount=0 and sii.uom='Piece' and is_return=0 order by si.posting_date
					 		""",values={"customer":self.customer,"item_code":item["item_code"],"uom":item["uom"]},as_dict=True)
		
		if not fifo:
			return f"Can't find any qty to mark return for item_code {item['item_code']} and uom {item['uom']} "
		for i in fifo:
			balance_qty=i['balance_qty']
			if balance_qty:
				if remaining_qty>0:
					if remaining_qty>=balance_qty:
						remaining_qty-=i['balance_qty']
						qty=i['balance_qty']
					else:
						qty=remaining_qty
						remaining_qty=0
					self.create_return(source_doc_name=i['name'],child_name=i["child_name"],qty=qty)
				else:
					break
		if remaining_qty:
			return f"For item code {item['item_code']} and uom {item['uom']}, {item['qty']-remaining_qty} quantity has been added, while the remaining {remaining_qty} cannot be added."
		return

	@frappe.whitelist()
	def remove_stock_out_qty(self):
		to_remove=[]
		if self.set_warehouse and self.update_stock==0:
			frappe.msgprint(" Please Set Warehouse ")
			return
		for item in self.items:
			try:
				bin=frappe.db.sql(""" select b.actual_qty from `tabBin` as b where b.warehouse=%(warehouse)s and b.item_code=%(item_code)s """,values={'warehouse':self.set_warehouse,'item_code':item.item_code})
				bin_qty=bin[0][0]
				if bin_qty < 1:
					to_remove.append(item.idx)
				elif bin_qty < item.qty :
					item.qty=bin_qty
			except:
				pass

		self.run_method("set_missing_values")
		self.run_method("calculate_taxes_and_totals")
		if self.name[0:3]!='new':
			self.save()
		return to_remove

def map_child_doc(source_d, target_parent, table_map, qty,source_parent=None,):
	target_child_doctype = table_map["doctype"]
	target_parentfield = target_parent.get_parentfield_of_doctype(target_child_doctype)
	target_d = frappe.new_doc(
		target_child_doctype, parent_doc=target_parent, parentfield=target_parentfield
	)

	map_doc(source_d, target_d, table_map, qty,target_parent,source_parent)

	target_d.idx = None
	target_parent.append(target_parentfield, target_d)
	return target_d


def map_doc(source_doc, target_doc, table_map, qty,target_parent,source_parent=None):
	if table_map.get("validation"):
		for key, condition in table_map["validation"].items():
			if condition[0] == "=" and source_doc.get(key) != condition[1]:
				frappe.throw(
					_("Cannot map because following condition fails:") + f" {key}={cstr(condition[1])}"
				)

	map_fields(source_doc, target_doc, table_map, source_parent)

	if "postprocess" in table_map:
		table_map["postprocess"](source_doc, target_doc, qty,target_parent,source_parent)
