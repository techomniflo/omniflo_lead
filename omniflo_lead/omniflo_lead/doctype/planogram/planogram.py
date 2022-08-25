# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Planogram(Document):
	def validate(self):
		if self.get('items'):
			no_of_rows=set()
			for item in self.get('items'):
				no_of_rows.add(item.row)
		if len(no_of_rows)>self.max_rows:
			frappe.throw(f'Rows are greater than {self.max_rows}')
				
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
			print(table)
			print(shelf_structure)
			return table
		return "\n\n\n\n"

