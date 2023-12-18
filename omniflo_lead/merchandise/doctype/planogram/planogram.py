# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Planogram(Document):
	def validate(self):
		
		if self.asset_configuration=='Category':
			if self.get('items'):
				frappe.throw("Please remove items from shelf table beacuse items should in Category")
		else:
			if self.get('category_items'):
				frappe.throw("Please remove items from category table beacuse items should in Shelf")
	def before_save(self):
		li=[]
		if self.get('items'):
			for i in self.items:
				li.append([i.row,i.column,i.item_code,i.qty,i.brand,i.item_name])
		li.sort(key=lambda x: (x[0],x[1],x[4],x[5]))
		self.items=[]
		tentative_value=0
		for i in li:
			doc=frappe.get_doc('Item',i[2])
			tentative_value=tentative_value+(float(doc.mrp)*int(i[3]))
			self.append("items",{
					"row":i[0],
					"column":i[1],
					"item_code":i[2],
					"qty":i[3],
					"brand":i[4],
					"item_name":i[5]
				})
		self.tentative_value=tentative_value*0.75
				
	@frappe.whitelist()
	def fetch_html(self):
		index="""
		<html>
		<body>
		<div class="row main">
    				<div class="col-xs-12">
						<table class="table table-bordered">
							{% for rows,column in shelf_structure.items() %}

							<tr>
								{% for key,values in column.items() %}
									<td>Total Qty  {{ values[1] }}</td>
									<td>{{values[0] }}</td>
								{% endfor %}
							</tr>
							{% endfor %}
						</table>
					</div>
				</div>
				</body>
			</html>
				"""
		if self.get('items'):
			shelf_structure={}

			for item in self.get('items'):

				
				if item.row not in shelf_structure:
					shelf_structure[item.row]={item.column:[item.brand,int(item.qty)]}
				elif item.column not in shelf_structure[item.row]:
					shelf_structure[item.row][item.column]=[item.brand,int(item.qty)]
				else:
					shelf_structure[item.row][item.column][1]+=int(item.qty)


			table=frappe.render_template(index,{'shelf_structure':shelf_structure})
			return table
		return "\n\n\n\n"

	@frappe.whitelist()
	def add_cohort(self):
		row=self.row
		column=self.column
		cohort=self.cohort
		cohort_items=frappe.db.sql(""" select item_code,qty from `tabCohort Items` where parent = %(cohort)s order by qty,item_code
		""",values={'cohort':cohort},as_list=True)
		for item in cohort_items:
			item_name,brand=frappe.db.sql("""select item_name,brand from `tabItem` where item_code=%(item_code)s order by brand,item_name""",values={'item_code':item[0]},as_list=True)[0]
			self.append('items',{
				'row':int(row),
				'column':int(column),
				'item_code':item[0],
				'item_name':item_name,
				'brand':brand,
				'qty':item[1]

			})

