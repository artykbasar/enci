# Copyright (c) 2021, Artyk Basarov and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from enci.erpnext_custom_integrations.custom.item_group import add_item_group_values_from_sql, after_migrate_item_group_edit, add_item_group_values_from_csv, add_item_group_values_from_csv_with_doctype


class ENCISettings(Document):
    @frappe.whitelist()
    def load_item_group_presets(self):
        # after_migrate_item_group_edit()
        # add_item_group_values_from_sql(self)
        # add_item_group_values_from_csv(self)
        # add_item_group_values_from_csv_with_doctype(self)
        function_path = "enci.erpnext_custom_integrations.custom.item_group.add_item_group_values_from_csv_with_doctype"
        frappe.enqueue(function_path, timeout=30000, queue="short",
                       doc=self)
