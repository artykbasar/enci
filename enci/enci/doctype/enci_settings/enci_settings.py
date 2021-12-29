# Copyright (c) 2021, Artyk Basarov and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from enci.erpnext_custom_integrations.custom.item_group import add_item_group_values_from_sql, after_migrate_item_group_edit

class ENCISettings(Document):
	@frappe.whitelist()
	def load_item_group_presets(self):
		after_migrate_item_group_edit()
		add_item_group_values_from_sql(self)

