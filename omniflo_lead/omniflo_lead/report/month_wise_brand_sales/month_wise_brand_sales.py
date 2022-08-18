# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

# import frappe
import frappe
import json
import time
import datetime
import copy
from collections import defaultdict
from omniflo_lead.omniflo_lead.report.overall_brand_sales.overall_brand_sales import Date_wise_sale


def execute(filters=None):
	columns = ["Month","Year","Brand","GMV","Store Live"]
	return columns, sales_month_wise()

@frappe.whitelist()
def sales_month_wise():
	live_store=frappe.db.sql("""SELECT `TabItem`.`brand` AS `brand`, count(distinct `tabCustomer Bin`.`customer`) AS `count`
FROM `tabCustomer Bin`
LEFT JOIN `tabItem` `TabItem` ON `tabCustomer Bin`.`item_code` = `TabItem`.`item_code` LEFT JOIN `tabCustomer` `TabCustomer` ON `tabCustomer Bin`.`customer` = `TabCustomer`.`name`
WHERE (`tabCustomer Bin`.`available_qty` > 0
   AND (`TabCustomer`.`customer_status` <> 'Closed'
    OR `TabCustomer`.`customer_status` IS NULL) AND `TabItem`.`brand` IS NOT NULL AND (`TabItem`.`brand` <> '' OR `TabItem`.`brand` IS NULL))
GROUP BY `TabItem`.`brand`
ORDER BY `TabItem`.`brand` ASC""",as_dict=True)
	brand_store_live={}
	for i in live_store:
		brand_store_live[i['brand']]=i['count']
	
	sales = Date_wise_sale()
	month_wise_sale={}
	for i in sales:
		month_year=i[0][3:]
		if month_year not in month_wise_sale:
			month_wise_sale[month_year]={i[4]:i[3]*(float(i[5]))}
		elif i[4] not in month_wise_sale[month_year]:
			month_wise_sale[month_year][i[4]]=i[3]*(float(i[5]))
		else:
			month_wise_sale[month_year][i[4]]+=i[3]*(float(i[5]))
	return_value=[]
	for month in list(month_wise_sale.keys()):
		for brand in list(month_wise_sale[month].keys()):
			temp=[month[0:2],month[3:],brand,month_wise_sale[month][brand],brand_store_live[brand]]
			return_value.append(temp)
	return return_value