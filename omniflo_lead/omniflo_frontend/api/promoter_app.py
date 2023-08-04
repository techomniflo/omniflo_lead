import frappe
import json
import copy
from frappe.utils import random_string,now
from datetime import datetime,date

def upload_file(doc,field_name,content,image_format):
	file_name=random_string(8)

	file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": file_name+"."+image_format,
				"attached_to_doctype": doc.doctype,
				"attached_to_name": doc.name,
				"attached_to_field": field_name,
				"folder": "Home/Attachments",
				"is_private": 1,
				"content": content,
				"decode": 1,
			}
		).save(ignore_permissions=True)
	url=copy.copy(file.file_url)
	return url

def create_promoter_hygiene(pl_name,req_data):
	promoter_hygiene = frappe.get_doc(
			{
				"doctype": "Promoter Hygiene",
				"promoter_log":pl_name,
				"check_in_category_placement": req_data["check_in_category_placement"],
				"set_merchandising": req_data["set_merchandising"],
				"set_offers": req_data["set_offers"],
				"set_per_planogram": req_data["set_per_planogram"],
				"clean_products_and_shelf": req_data["clean_products_and_shelf"],
				"check_uniform_and_id_card": req_data["check_uniform_and_id_card"],
			}
		).save(ignore_permissions=True)
	try:
		if "selfie" in req_data and len(req_data["selfie"])>0:
			if len(req_data["selfie"][0]):
				image_format=req_data["selfie"][0]["format"]
				selfie_url=upload_file(doc=promoter_hygiene,field_name="selfie",content=req_data["selfie"][0]["base64"],image_format=image_format)
				promoter_hygiene.append('capture_all_asset',{'image':selfie_url,'type':'Selfie'})

		for i in req_data["capture_all_asset"]:
			image_format=i["format"]
			url=upload_file(promoter_hygiene,"image",i["base64"],image_format)
			promoter_hygiene.append("capture_all_asset",
				{"image":url,'type':'Asset'})
		promoter_hygiene.save(ignore_permissions=True)
	except Exception:
		return "Your Attendance is marked but there is some issue in image ."
	return


@frappe.whitelist(allow_guest=True)
def create_promoter_log(**kwargs):
	kwargs = json.loads(frappe.request.data)
	if "is_present" in kwargs:
		if kwargs["is_present"]==1:
			check_list=["promoter","customer","latitude","longitude","event_type"]
			for i in check_list:
				if i not in kwargs.keys():
					frappe.local.response['http_status_code'] = 404
					return "Some fields missing"
		elif kwargs["is_present"]==0:
			check_list=["leave_type","duration","reason"]
			for i in check_list:
				if i not in kwargs.keys():
					frappe.local.response['http_status_code'] = 404
					return "Some fields missing"
	
	promoter_log= frappe.new_doc('Promoter Log')
	try:
		promoter_doc=frappe.get_doc('Promoter',kwargs['promoter'])
	except Exception:
		frappe.local.response['http_status_code'] = 404
		return f"Promoter {kwargs['Promoter']} not Found."
	
	promoter_log.promoter_name=promoter_doc.full_name
	promoter_log.item_group=promoter_doc.item_group
	promoter_log.promoter=kwargs['promoter']
	promoter_log.is_present=kwargs['is_present']
	if kwargs['is_present']==1:
		promoter_log.customer=kwargs['customer']

		try:
			customer=frappe.get_doc('Customer',kwargs['customer'])
		except Exception:
			frappe.local.response['http_status_code'] = 404
			return f"Promoter {kwargs['Customer']} not Found."
		
		promoter_log.customer_name=customer.customer_name
		promoter_log.latitude=kwargs['latitude']
		promoter_log.longitude=kwargs['longitude']
		promoter_log.event_type=kwargs['event_type']
		if "accuracy" in kwargs:
			promoter_log.accuracy=kwargs['accuracy']
		if 'fingerprint' in kwargs:
			promoter_log.fingerprint=kwargs['fingerprint']
	else:
		promoter_log.leave_type=kwargs['leave_type']
		promoter_log.duration=kwargs['duration']
		if 'duration' in kwargs:
			promoter_log.reason=kwargs['reason']
	promoter_log.save(ignore_permissions=True)
	if kwargs["is_present"]==1:
		if kwargs["event_type"]=="check in":
			frappe.enqueue(create_promoter_hygiene,pl_name=promoter_log.name,req_data=kwargs)
	frappe.local.response['http_status_code'] = 201
	return promoter_log

@frappe.whitelist(allow_guest=True)
def create_promoter_sales_capture(**kwargs):
	kwargs = json.loads(frappe.request.data)
	psc_doc = frappe.new_doc('Promoter Sales Capture')
	check_list=["promoter","customer","qty","brand","item_name","item_code","age","gender","in_category"]
	for i in check_list:
		if i not in kwargs:
			frappe.local.response['http_status_code']=404
			return "Some fields are missing."
	psc_doc.customer=kwargs['customer']
	psc_doc.promoter=kwargs['promoter']
	psc_doc.qty=kwargs['qty']
	psc_doc.brand=kwargs['brand']
	psc_doc.item_name=kwargs['item_name']
	psc_doc.item_code=kwargs['item_code']
	if 'age' in kwargs:
		psc_doc.age=kwargs['age']
	if 'gender' in kwargs:
		psc_doc.gender=kwargs['gender']
	if 'in_category' in kwargs:
		psc_doc.in_category=kwargs['in_category']
	if 'posting_date' in kwargs:
		pass
	else:
		psc_doc.posting_date=now()
	psc_doc.save(ignore_permissions=True)
	frappe.local.response['http_status_code'] = 201
	return psc_doc

@frappe.whitelist(allow_guest=True)
def get_customer_location():
	values={"customer":frappe.request.args["customer"]}
	return frappe.db.sql("select cp.latitude,cp.longitude from `tabCustomer Profile` as cp where cp.customer=%(customer)s",values=values,as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_items(customer):
	values={"customer":customer}
	data=frappe.db.sql("""select i.sub_brand,i.item_name,i.item_code,i.mrp from `tabSales Invoice` as si join `tabSales Invoice Item` as sii on si.name=sii.parent join `tabItem` as i on i.item_code=sii.item_code where i.brand not in ('Sample','Tester') and si.docstatus=1 and si.customer=%(customer)s and 0<(select sum(SII.qty) from `tabSales Invoice` as SI join `tabSales Invoice Item` as SII on SI.name=SII.parent where SI.docstatus=1 and SI.company=si.company and SI.customer=si.customer and SII.item_code=sii.item_code) group by i.sub_brand,i.item_name,i.item_code,i.mrp
		    		
		    		union
	
				select i.sub_brand,i.item_name,i.item_code,i.mrp from `tabThird Party Invoicing` as tpi join `tabThird Party Invoicing Item` as tpii on tpi.name=tpii.parent join `tabItem` as i on i.item_code=tpii.item_code where tpi.docstatus=1 and tpi.customer=%(customer)s
		    	
		    """,values=values,as_dict=True)
	brand_details={}
	for i in data:
		if i['sub_brand'] not in brand_details:
			brand_details[i['sub_brand']]=[(i['item_name'],"mrp:- "+str(i['mrp']),i['item_code'])]
		else:
			brand_details[i['sub_brand']].append((i['item_name'],"mrp:- "+str(i['mrp']),i['item_code']))
	return brand_details

@frappe.whitelist(allow_guest=True)
def today_promoters_log():
	values={"promoter":frappe.request.args["promoter"]}
	return frappe.db.sql("""select pl.creation,pl.promoter,pl.customer,pl.event_type,pl.is_present,pl.latitude,pl.longitude from `tabPromoter Log` as pl where pl.promoter=%(promoter)s and date(pl.creation)=curdate() order by pl.creation """,values=values,as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_target():
	values={"promoter":frappe.request.args["promoter"]}
	wtd=frappe.db.sql(""" select date(pl.creation) as date,pl.promoter,pl.customer,pl.item_group,ct.target/day(ct.end_date) as per_day_target,(select sum(i.mrp*psc.qty) from `tabPromoter Sales Capture` as psc join `tabItem` as i on i.item_code=psc.item_code where psc.promoter=pl.promoter and date(psc.posting_date)=date(pl.creation) ) as gmv from `tabPromoter Log` as pl join `tabCustomer Target` as ct on ct.item_group=pl.item_group and date(pl.creation) between ct.start_date and ct.end_date join `tabCustomer Target Item` as cti on cti.customer=pl.customer and cti.parent=ct.name where is_present=1 and week(curdate(),1)=week(pl.creation,1) and year(curdate())=year(pl.creation) and pl.promoter=%(promoter)s group by pl.customer,pl.promoter,date(pl.creation) order by date(pl.creation)""",values=values,as_dict=True)
	current_date=frappe.db.sql("""select ct.target/day(ct.end_date) as target,(select sum(i.mrp*psc.qty) from `tabPromoter Sales Capture` as psc join `tabItem` as i on i.item_code=psc.item_code where psc.promoter=pl.promoter and date(psc.creation)=date(pl.creation) ) as gmv from `tabPromoter Log` as pl join `tabCustomer Target` as ct on ct.item_group=pl.item_group and date(pl.creation) between ct.start_date and ct.end_date join `tabCustomer Target Item` as cti on cti.customer=pl.customer and cti.parent=ct.name where is_present=1 and date(pl.creation)=curdate() and pl.promoter=%(promoter)s group by pl.customer,pl.promoter,date(pl.creation) order by date(pl.creation)""",values=values,as_dict=True)
	days=6
	total_wtd_target=0
	total_wtd_gmv=0
	for i in wtd:
		if i["gmv"]==None:
			i["gmv"]=0
		if i["per_day_target"]==None:
			i["per_day_target"]=0
		total_wtd_gmv+=i["gmv"]
		total_wtd_target+=i["per_day_target"]
		days-=1
	if days and len(wtd)>0:
		total_wtd_target+=days*wtd[-1]["per_day_target"]
	if len(current_date)==0:
		return {"week":{"target":total_wtd_target,"gmv":total_wtd_gmv},"today":{"target":0,"gmv":0}}
	return {"week":{"target":total_wtd_target,"gmv":total_wtd_gmv},"today":{"target":current_date[0]["target"] or 0,"gmv":current_date[0]["gmv"] or 0}}

@frappe.whitelist(allow_guest=True)
def log():
	values={"promoter":frappe.request.args["promoter"]	}
	pl_data=frappe.db.sql(""" select date(pl.creation) as date,time(pl.creation) as time,pl.is_present,pl.promoter,pl.customer,pl.event_type from `tabPromoter Log` as pl where pl.promoter=%(promoter)s and month(curdate())=month(pl.creation) and year(pl.creation)=year(curdate()) order by pl.creation """,values=values,as_dict=True)
	pl_gmv_data=frappe.db.sql(""" select date(psc.creation) as date,sum(psc.qty*i.mrp) as gmv from `tabPromoter Sales Capture` as psc join `tabItem` as i on i.item_code=psc.item_code where psc.promoter=%(promoter)s and month(curdate())=month(psc.creation) and year(curdate())=year(psc.creation) group by date(psc.creation) """,values=values,as_dict=True)

	def has_no_event(dayLog,day_wise_time): 
		hour=find_diff_time(dayLog[0]["time"],dayLog[-1]["time"])
		day_wise_time[dayLog[0]['date']]=({'date':dayLog[0]['date'],'hours':hour,'gmv':0})
		return day_wise_time
		
	
	def has_event(dayLog,day_wise_time):
		in_event=["punch","end break","check in"]
		out_event=["start break","check out"]
		count_hours=0
		is_in_store=False
		for i in dayLog:
			if i["event_type"] in in_event and is_in_store==False:
				is_in_store=True
				last_in_time=i["time"]
			
			if i["event_type"] in out_event and is_in_store==True:
				count_hours+=find_diff_time(last_in_time,i["time"])
				is_in_store=False
		if is_in_store == True:
			count_hours+=find_diff_time(last_in_time, dayLog[-1]["time"])

		day_wise_time[dayLog[0]['date']]=({'date':dayLog[0]['date'],'hours':count_hours,'gmv':0})
		return day_wise_time

	def find_diff_time(time1,time2):
		sec = time2-time1
		sec = sec.total_seconds()
		hour = sec/(60*60)
		return hour
	
	def calculate_hours(day_wise_time={}):
		check_event=0
		day=pl_data[0]['date']
		dayLog=[]
		for count, ele in enumerate(pl_data):
			if day!=ele['date'] or len(pl_data)-1==count:
				if len(pl_data)-1==count and day==ele['date']:
					dayLog.append(ele)
				if check_event:
					day_wise_time=has_event(dayLog,day_wise_time)
				else:
					day_wise_time=has_no_event(dayLog,day_wise_time)
				if ele["event_type"]==None or ele["event_type"]=="":
					check_event=0
				else:
					check_event=1
				day=ele['date']
				dayLog = []
			
			dayLog.append(ele)
		return day_wise_time
	if pl_data:
		log=calculate_hours()
	else:
		log=[]
	for i in pl_gmv_data:
		if i["date"] in log:
			log[i["date"]]["gmv"]=i["gmv"]
			
		else:
			log[i["date"]]={"date":i["date"],"gmv":i["gmv"],"hours":0}
	if not log:
		return []
	return_value=list(log.values())
	sorted_return_values = sorted(return_value, key=lambda x: x['date'])
	result = [dict(item, **{'average_variance':True}) for item in sorted_return_values]
	return result

@frappe.whitelist(allow_guest=True)
def top_promoter():
	promoter_doc=frappe.get_doc('Promoter',frappe.request.args["promoter"] )
	if promoter_doc.item_group==None or promoter_doc.item_group=="":
		return []
	values={"item_group":promoter_doc.item_group}
	yesterday=frappe.db.sql("""
								select 
									*, 
									(gmv / target)* 100 as percentage 
									from 
									(
										select 
										psc.customer, 
										sum(i.mrp * psc.qty) as gmv, 
										psc.promoter, 
										p.full_name, 
										date(posting_date) as posting_date, 
										(
											select 
											sum(ct.target)/ day(
												last_day(psc.posting_date)
											) 
											from 
											`tabCustomer Target` as ct 
											join `tabCustomer Target Item` as cti on cti.parent = ct.name 
											where 
											cti.customer = psc.customer 
											and (
												date(psc.posting_date) between ct.start_date 
												and ct.end_date
											) 
											and ct.item_group = p.item_group
										) as target 
										from 
										`tabPromoter Sales Capture` as psc 
										join `tabItem` as i on i.item_code = psc.item_code 
										join `tabPromoter` as p on p.name = psc.promoter 
										where 
										date(psc.posting_date)= curdate() - interval 1 day 
										and p.item_group = %(item_group)s
										group by 
										psc.promoter, 
										psc.customer, 
										date(psc.posting_date)
									) as meta 
									order by 
									percentage desc 
									limit 
									3""",values=values,as_dict=True)
	last_week=frappe.db.sql("""select 
									master_data.promoter,
									master_data.full_name, 
									sum(gmv) as gmv, 
									sum(target) as target, 
									(
										sum(gmv)/ sum(target)
									)* 100 as percentage 
									from 
									(
										select 
										log.*, 
										p.full_name, 
										(
											select 
											sum(psc.qty * i.mrp) 
											from 
											`tabPromoter Sales Capture` as psc 
											join `tabItem` as i on i.item_code = psc.item_code 
											where 
											psc.promoter = log.promoter 
											and psc.customer = log.customer 
											and date(psc.posting_date)= log.posting_date
										) as gmv, 
										(
											select 
											sum(ct.target)/ day(
												last_day(log.posting_date)
											) 
											from 
											`tabCustomer Target` as ct 
											join `tabCustomer Target Item` as cti on cti.parent = ct.name 
											where 
											cti.customer = log.customer 
											and (
												log.posting_date between ct.start_date 
												and ct.end_date
											) 
											and ct.item_group = p.item_group
										) as target 
										from 
										(
											select 
											date(pl.creation) as posting_date, 
											pl.promoter, 
											pl.customer 
											from 
											`tabPromoter Log` as pl 
											where 
											week(pl.creation, 1)= week(
												curdate()
											)-1 
											and year(pl.creation)= year(
												curdate()
											) 
											and is_present = 1 
											group by 
											pl.promoter, 
											pl.customer, 
											date(pl.creation) 
											union 
											select 
											date(psc.posting_date) as posting_date, 
											psc.promoter, 
											psc.customer 
											from 
											`tabPromoter Sales Capture` as psc 
											where 
											week(psc.posting_date, 1)= week(
												curdate()
											)-1 
											and year(psc.posting_date)= year(
												curdate()
											) 
											group by 
											psc.promoter, 
											psc.customer, 
											date(psc.posting_date)
										) as log 
										join `tabPromoter` as p on p.name = log.promoter 
										where 
										p.item_group = %(item_group)s
									) as master_data 
									group by 
									master_data.promoter 
									order by 
									percentage desc 
									limit 
									3
 				""",values=values,as_dict=True)
	return {"last_week":last_week,"yesterday":yesterday}

@frappe.whitelist(allow_guest=True)
def get_promoter_payment_log():
	""" This function returns a pending acknowledgement by the promoter. """
	values={"promoter":frappe.request.args["promoter"]}
	return frappe.db.sql("select ppl.name,ppl.processing_date,ppl.month,ppl.year,ppl.promoter,ppl.amount,ppl.payment_type from `tabPromoter Payment Log` as ppl where ppl.promoter=%(promoter)s and ppl.acknowledgement=0 and ppl.docstatus=1",values=values,as_dict=True)

@frappe.whitelist(allow_guest=True,methods=["POST"])
def post_promoter_payment_log():
	""" This is an acknowledgement function for the promoter to confirm that they have received the correct amount."""
	try:
		name=frappe.request.args["name"]
		latitude=frappe.request.args["latitude"]
		longitude=frappe.request.args["longitude"]
		ip_address=frappe.request.headers.get("X-Forwarded-For")
	except Exception:
		frappe.local.response['http_status_code'] = 404
		return 
	frappe.db.set_value('Promoter Payment Log', name, {
		'ip_address': ip_address,
		'latitude': latitude,
		'longitude':longitude,
    	'acknowledgement':1,
	    'timestamp':now()
	})
	frappe.db.commit()
	frappe.local.response['http_status_code'] = 201
	return frappe.db.get_value('Promoter Payment Log', name, ['acknowledgement'], as_dict=1)

@frappe.whitelist(allow_guest=True)
def get_offers():
	promoter=frappe.request.args["promoter"]
	promoter_doc=frappe.get_doc("Promoter",promoter)
	item_group=promoter_doc.item_group
	return frappe.db.sql("""select obo.brand,obo.offer from `tabOmniverse Brand Offer` obo where obo.disabled=0 and obo.brand in (select distinct i.brand from `tabItem` as i where i.item_group=%(item_group)s )""",values={'item_group':item_group},as_dict=True)

@frappe.whitelist(allow_guest=True)
def promoter_mtd_details(promoter):
	values={'promoter':promoter}
	attandance_punch=frappe.db.sql(""" select count(*) from (select * from `tabPromoter Log` as pl where pl.is_present=1 and month(pl.creation)=month(curdate()) and year(pl.creation)=year(curdate()) and date(pl.creation) not in ( select date(pl.creation) from `tabPromoter Log` as PL where date(PL.creation)=date(pl.creation) and pl.is_present=0 ) and pl.promoter=%(promoter)s group by date(pl.creation), pl.promoter) as meta """,values=values,as_list=True)
	total_leave=frappe.db.sql(""" select count(*) from (select * from `tabPromoter Log` as pl where pl.is_present=0 and month(pl.creation)=month(curdate()) and year(pl.creation)=year(curdate()) and pl.promoter=%(promoter)s group by date(pl.creation), pl.promoter) as meta """,values=values,as_list=True)
	weekoff_leave=frappe.db.sql(""" select count(*) from (select * from `tabPromoter Log` as pl where pl.is_present=0 and month(pl.creation)=month(curdate()) and year(pl.creation)=year(curdate()) and leave_type='Week Off' and pl.promoter=%(promoter)s  group by date(pl.creation), pl.promoter) as meta """,values=values,as_list=True)
	weekend_leave=frappe.db.sql(""" select count(*) from (select * from `tabPromoter Log` as pl where pl.is_present=0 and month(pl.creation)=month(curdate()) and year(pl.creation)=year(curdate()) and weekday(pl.creation) in (5,6) and pl.promoter=%(promoter)s group by date(pl.creation), pl.promoter) as meta """,values=values,as_list=True)
	return {'attandance_punch':attandance_punch[0][0],'total_leave':total_leave[0][0],'weekoff_leave':weekoff_leave[0][0],'weekend_leave':weekend_leave[0][0],'percentage_attandance':(attandance_punch[0][0]/date.today().day)*100}