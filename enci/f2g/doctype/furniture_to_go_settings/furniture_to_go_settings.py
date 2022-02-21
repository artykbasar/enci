# -*- coding: utf-8 -*-
# Copyright (c) 2021, Artyk Basarov and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import enci
import frappe
from enci.api import backgroud_jobs_check
# import enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods as f2g
from frappe.model.document import Document

class FurnitureToGoSettings(Document):
	@frappe.whitelist()
	def find_new_products(self):
		if self.enable == 1:
			function_path = "enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods.find_new_products"
			backgroud_jobs_check(function_path)
			frappe.enqueue(function_path, timeout=30000, queue="long", 
							docname=self.doctype, field_name="sync_products", id="f2g_settings")

	@frappe.whitelist()
	def find_product_group(self):
		if self.enable == 1:
			function_path = "enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods.product_group_finder"
			backgroud_jobs_check(function_path)
			frappe.enqueue(function_path, timeout=30000, queue="long", 
							docname=self.doctype, field_name="sync_groups", id="f2g_settings")

	@frappe.whitelist()
	def find_product_range(self):
		if self.enable == 1:
			function_path = 'enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods.product_range_finder'
			backgroud_jobs_check(function_path)
			frappe.enqueue(function_path, timeout=30000, queue="long", 
							docname=self.doctype, field_name="sync_ranges", id="f2g_settings")


	@frappe.whitelist()
	def sync_products_to_items(self):
		if self.enable == 1:
			frappe.enqueue('enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods.f2g_to_item', timeout=30000)
	
	@frappe.whitelist()
	def auto_fill_defaults(self):
		if self.enable == 1:
			from enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods import default_f2g_values
			default_f2g_values()
			self.reload()
	
	@frappe.whitelist()
	def tester(self):
		if self.enable == 1:
			from enci.f2g.doctype.furniture_to_go_settings.furniture_to_go_methods import create_folder_in_files
			create_folder_in_files('product_images_2')


