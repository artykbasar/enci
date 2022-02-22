# Copyright (c) 2021, Artyk Basarov and contributors
# For license information, please see license.txt

import json
import frappe, datetime
from frappe.model.document import Document
from frappe.exceptions import DoesNotExistError
from frappe import _
from dateutil import parser
from enci import backgroud_jobs_check, publish_progress
try:
	from enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods import f2g_ins, download_file
except:
	pass


@frappe.whitelist()
def sync_f2g_to_item(doc: str):
	frappe.only_for("System Manager")
	doc = json.loads(doc)
	f2g_item = frappe.get_doc("Furniture To Go Products", doc.get("name"))
	f2g_item.sync_product_to_f2g()
	f2g_item.sync_f2g_to_item()
	return doc

@frappe.whitelist()
def sync_f2g_to_item_list(names):
	frappe.only_for("System Manager")
	docs = json.loads(names)
	total_len = len(docs)
	for index, doc in enumerate(docs):
		doc_name = "Furniture To Go Products"
		publish_progress(doc_name, "f2g_products_sync", index+1, total_len, f"{doc} currently being synced with F2G")
		doc_item = frappe.get_doc(doc_name, doc)
		doc_item.sync_product_to_f2g()
		publish_progress(doc_name, "f2g_products_sync", index+1, total_len, f"{doc} currently being synced with Item")
		doc_item.sync_f2g_to_item()
		publish_progress(doc_name, "f2g_products_sync", index+1, total_len, f"{doc} syncing is done")

@frappe.whitelist()
def sync_f2g_to_item_list_enqueue(names):
	function_path = "enci.f2g.doctype.furniture_to_go_products.furniture_to_go_products.sync_f2g_to_item_list"
	backgroud_jobs_check(function_path)
	frappe.enqueue(function_path, timeout=30000, queue="long", names=names)

@frappe.whitelist()
def sync_all_f2g_products():
	names = frappe.db.get_list("Furniture To Go Products", pluck="name")
	sync_f2g_to_item_list_enqueue(names)


class FurnitureToGoProducts(Document):

	def __init__(self, *args, **kwargs):
		super(FurnitureToGoProducts, self).__init__(*args, **kwargs)
		self.f2g_settings_doc = None

	# def validate(self):
	# 	self.sync_f2g_to_item()

	def f2g_settings(self):
		if not self.f2g_settings_doc:
			self.f2g_settings_doc = frappe.get_doc('Furniture To Go Settings')
		return self.f2g_settings_doc

	@frappe.whitelist()
	def sync_to_f2g(self):
		self.sync_product_to_f2g()
		self.reload()

	@frappe.whitelist()
	def sync_f2g_to_item_button(self):
		self.sync_f2g_to_item(button=True)

	def sync_f2g_to_item(self, button=None):
		if self.discontinued:
			if button:
				frappe.msgprint(_("This Product will not be synced with Item as Discontinued field has been checked."),
				indicator="red")
		else:
			try:
				item = frappe.get_doc("Item", self.item)
				save_type = True
			except DoesNotExistError:
				item = frappe.new_doc("Item")
				save_type = False
			except AttributeError:
				item_check = frappe.db.get_list(
					"Item Supplier",
            		filters={
            		'supplier_part_no': self.name
            		}, 
            		fields=['parent'])
				if item_check:
					item_code = item_check[0]['parent']
					item = frappe.get_doc('Item', item_code)
					save_type = True
				else:
					item = frappe.new_doc("Item")
					save_type = False
			save_status = False
			if not self.brand:
				brand = self.f2g_settings().default_brand
			else:
				brand = self.brand
			if not self.item_group:
				f2g_group = self.f2g_settings().item_group
			else:
				f2g_group = self.item_group
			if not save_type or item.item_group != f2g_group:
				item.item_group = f2g_group
				save_status = True
			if  not save_type or item.item_name != self.product_name:
				item.item_name = self.product_name
				save_status = True
			if not save_type or item.brand != brand:
				item.brand = brand
				save_status = True
			if not save_type or item.description != self.description:
				item.description = self.description
				save_status = True
			if not save_type or item.image != self.main_image:
				item.image = self.main_image
				save_status = True
			if self.box:
				for each_item_box in self.box:
					if not save_type or not item.item_box:
						item.append('item_box',{
                            'box_number': each_item_box.box_number,
                            'box_ean': each_item_box.barcode,
                            'box_height': each_item_box.height,
                            'box_width': each_item_box.width,
                            'box_depth': each_item_box.depth,
                            'box_dim_unit': each_item_box.unit,
                            'box_weight': each_item_box.weight
                        })
						save_status = True
					else:
						box = item.item_box[each_item_box.idx - 1]
						if box.box_ean != each_item_box.barcode:
							box.box_ean = each_item_box.barcode
							save_status = True
						if float(box.box_height) != float(each_item_box.height):
							box.box_height = float(each_item_box.height)
							save_status = True
						if float(box.box_width) != float(each_item_box.width):
							box.box_width = float(each_item_box.width)
							save_status = True
						if float(box.box_depth) != float(each_item_box.depth):
							box.box_depth = float(each_item_box.depth)
							save_status = True
						if box.box_dim_unit != each_item_box.unit:
							box.box_dim_unit = each_item_box.unit
							save_status = True
						if float(box.box_weight) != float(each_item_box.weight):
							box.box_weight = each_item_box.weight
							save_status = True
			default_lead_time = int(self.f2g_settings().default_lead_time)
			lead_time = 365
			if self.next_delivery:
				if type(self.next_delivery) == str:
					lead_time = parser.parse(self.next_delivery).date() - datetime.datetime.today().date()
				else:
					lead_time = self.next_delivery - datetime.datetime.today().date()
				lead_time = lead_time.days + default_lead_time
			elif int(self.stock_level) > 0:
				lead_time = default_lead_time
			if not save_type or int(item.lead_time_days) != int(lead_time):
				item.lead_time_days = lead_time
				save_status = True 
			if not save_type:
				item.append('supplier_items',
					{'supplier': self.f2g_settings().default_supplier,
					'supplier_part_no': self.product_sku
					})
				item = item.insert(ignore_permissions=True)
				self.item = item.name
				self.save()
			elif save_status:
				item = item.save()
				if not self.item:
					self.item = item.name
		return self

	def sync_product_to_f2g(self):
		product_details = f2g_ins.product_data_extractor(self.supplier_url)
		print(product_details)
		if product_details['status'] != 200:
			self.discontinued = 1
			self.save(ignore_permissions=True)
			return self
		edited = False
		# product_sku is being compared in F2G site. If there are any changes it will be changed to New value.
		if self.product_sku != product_details['sku']:
			self.product_sku = product_details['sku']
			edited = True
		# product_name is being compared in F2G site. If there are any changes it will be changed to New value.
		if self.product_name != product_details['product_name']:
			self.product_name = product_details['product_name']
			edited = True
		# next_delivery_date is being compared in F2G site. If there are any changes it will be changed to New value.
		if product_details['stock']['next_delivery_date']:
			parsed_date_del_date = parser.parse(product_details['stock']['next_delivery_date'], dayfirst=True)
			if self.next_delivery != parsed_date_del_date.strftime("%Y-%m-%d"):
				self.next_delivery = parsed_date_del_date.strftime("%Y-%m-%d")
				edited = True
		# availability is being compared in F2G site. If there are any changes it will be changed to New value. 
		if self.availability != product_details['stock']['stock_status']:
			self.availability = product_details['stock']['stock_status']
			edited = True
		# stock_level is being compared in F2G site. If there are any changes it will be changed to New value.  
		if int(self.stock_level) != int(product_details['stock']['qty']):
			self.stock_level = product_details['stock']['qty']
			edited = True
		# barcode is being compared in F2G site. If there are any changes it will be changed to New value. 
		if self.barcode != product_details['ean'] and not self.manual_barcode_entry:
			self.barcode = product_details['ean']
			edited = True
		# Box is being compared in F2G site. If there are any changes it will be changed to New value.
		if product_details['box'] and not self.manual_box_entry:
			box_keys = product_details["box"].keys()
			box_int = 0
			for box_key in box_keys:
				height, width, length, unit, weight, box_ean = ['', '', '', '', '', '']
				if product_details['box'][box_key].get('box_dimensions'):
					height = product_details['box'][box_key]['box_dimensions']['height']
					width = product_details['box'][box_key]['box_dimensions']['width']
					length = product_details['box'][box_key]['box_dimensions']['length']
					unit = product_details['box'][box_key]['box_dimensions']['unit']
				if product_details['box'][box_key].get('box_weight'):
					weight = product_details['box'][box_key]['box_weight']
				if product_details['box'][box_key].get('box_ean_code'):
					box_ean = product_details['box'][box_key]['box_ean_code']
				if box_int < len(self.box):
					# Box height is being compared in F2G site. If there are any changes it will be changed to New value.
					if height:
						if float(self.box[box_int].height) != float(height):
							self.box[box_int].height = height
							edited = True
					# Box width is being compared in F2G site. If there are any changes it will be changed to New value.
					if width:
						if float(self.box[box_int].width) != float(width):
							self.box[box_int].width = width
							edited = True
					# Box depth is being compared in F2G site. If there are any changes it will be changed to New value.
					if length:
						if float(self.box[box_int].depth) != float(length):
							self.box[box_int].depth = length
							edited = True
					# Box unit is being compared in F2G site. If there are any changes it will be changed to New value.
					if unit:
						if self.box[box_int].unit != unit:
							self.box[box_int].unit = unit
							edited = True
					# Box weight is being compared in F2G site. If there are any changes it will be changed to New value.
					if weight:
						if float(self.box[box_int].weight) != float(weight):
							self.box[box_int].weight = weight
							edited = True
				else:
					# If this box was not imported before, it will be imported.        
					self.append('box',
								{'box_number': box_int + 1,
								'barcode': box_ean,
								'height': height,
								'width': width,
								'depth': length,
								'unit': unit,
								'weight': weight})
					edited = True
				box_int += 1
		# Requsting from database bullet_points for the each item.
		bullet_check_tuples = frappe.db.get_list('Furniture To Go Product Bullet Points',
											filters={
												'parent': self.name
											},
											fields=['bullet_point'],
											as_list=True
										)
		# As database returns the results in tuple, we need a list. We are converting it to a list.
		bullet_check = []
		if bullet_check_tuples:
			for bullet_check_tuple in list(bullet_check_tuples):
				bullet_check.append(list(bullet_check_tuple)[0])
		# bullet_point is being compared in F2G site. If there are any changes it will be changed to New value.
		if product_details['product_bullet_points']:
			for bullet_point in product_details['product_bullet_points']:
				if bullet_point not in bullet_check:
					self.append('product_bullet_points',{'bullet_point': bullet_point})
					edited = True
		attachments = self.get_value('product_attachments')
		attachment_list = []
		for each in attachments:
			attachment_list.append(each.f2g_attachment_file)
		change_detected = False
		if product_details['product_file']:
			for product_file in product_details['product_file']:
				if product_file['link'] not in attachment_list:
					change_detected = True
					break
		
		if change_detected:
			self.product_attachments = None
			for product_file in product_details['product_file']:
				try:
					downloaded_file = download_file(product_file['link'], "Home/Attachments", True)
					self.append('product_attachments',{'attachment_name': downloaded_file["file_name"],
														'attachment_file': downloaded_file["file_url"],
														'f2g_attachment_file': product_file['link']})
				except KeyError:
					pass
			edited = True
		
		change_detected = False
		images = product_details['product_images']
		if images:
			item_images = self.get_value('product_images')
			item_image_list = []
			for each in item_images:
				item_image_list.append(each.f2g_image_file)
			for i in range(len(images)):
				if images[i] not in item_image_list:
					change_detected = True
					break
		if change_detected:
			self.product_images = None
			f2g_main_image = product_details['product_images'][0]
			self.f2g_main_image = f2g_main_image
			self.main_image = download_file(f2g_main_image, 'Home/product_images')['file_url']
			for i in range(len(images)):
				download_image = download_file(images[i], 'Home/product_images')
				self.append('product_images', {'image_name': download_image['file_name'],
												'image_file': download_image['file_url'],
												'f2g_image_file': images[i]})
			edited = True

		if self.supplier_url != product_details['product_link']:
			self.supplier_url = product_details['product_link']
			edited = True
		if self.description != product_details['product_description']:
			self.description = product_details['product_description']
			edited = True
		price = product_details['prices']
		hd_price = price['home_delivery']
		store_price = price['store_delivery']
		over_250 = price['order_over_250']
		over_500 = price['order_over_500']
		over_1000 = price['order_over_1000']
		over_2000 = price['order_over_2000']
		if hd_price != self.hd_price:
			self.hd_price = hd_price
			edited = True
		if store_price != self.store_delivery_price:
			self.store_delivery_price = store_price
			edited = True
		if over_250 != self.over_250:
			self.over_250 = over_250
			edited = True
		if over_500 != self.over_500:
			self.over_500 = over_500
			edited = True
		if over_1000 != self.over_1000:
			self.over_1000 = over_1000
			edited = True
		if over_2000 != self.over_2000:
			self.over_2000 = over_2000
			edited = True
		# print(product_details)
		if edited:
			self.save(ignore_permissions=True)
		return self
