# Copyright (c) 2022, Omniflo and contributors
# For license information, please see license.txt

import frappe
from omniflo_lead.omniflo_lead.report.mtd_customer_sales.mtd_customer_sales import mtd_sales


def execute(filters=None):
	columns=["Agent Name","MTD Sales","Overall Sales","Number of Stores"]
	return columns,

def mtd_agent_sales():
	sales_data=mtd_sales()
	agent_sales={}
	for i in sales_data:
		if i[4]=='null' or i[4]==None or i[4]=="":
			agent="Not Defined"
		else:
			agent=i[4]
		if agent not in agent_sales:
			agent_sales[agent]=[i[4],i[1],i[2],1]
		else:
			agent_sales[agent][3]+=1
			agent_sales[agent][1]+=i[1]
			agent_sales[agent][2]+=i[2]
	return list(agent_sales.values())
