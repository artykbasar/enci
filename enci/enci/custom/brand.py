from typing import Generic
import frappe
from erpnext.setup.doctype.brand.brand import Brand


class ENCIBrand(Brand):
    def validate(self):
        if self.brand and not self.brand_id:
            brand_id = ""
            if len(self.brand) < 4:
                min_len = True
                while min_len:
                    brand_id = f"{brand_id}{self.brand}"
                    if len(brand_id) > 3:
                        min_len = False
            else:
                brand_id = self.brand
            self.brand_id = brand_id[0:4].upper()
        elif self.brand_id:
            if len(self.brand_id) != 4:
                frappe.throw("Brand ID has to be 4 characters long")
            self.brand_id = self.brand_id.upper()
            

def after_migrate_brand_edit():
    add_custom_fields()
    set_default_brand()


def add_custom_fields():
    brand_id_check = frappe.db.exists('Custom Field', 'Brand-brand_id')
    brand_id_in_items_check = frappe.db.exists('Custom Field', 'Item-brand_id')
    if not brand_id_check:
        doc = frappe.new_doc('Custom Field')
        doc.dt = "Brand"
        doc.label = "Brand ID"
        doc.fieldname = "brand_id"
        doc.insert_after = "brand"
        doc.fieldtype = "Data"
        doc.length = 4
        doc.reqd = 0
        doc.unique = 1
        doc.in_list_view = 1
        doc.in_standard_filter = 1
        doc.in_global_search = 1
        doc.in_preveiw = 1
        doc.allow_in_quick_entry = 1
        doc.insert(ignore_permissions=True)
    if not brand_id_in_items_check:
        doc_items = frappe.new_doc('Custom Field')
        doc_items.dt = "Item"
        doc_items.label = "Brand ID"
        doc_items.fieldname = "brand_id"
        doc_items.insert_after = "brand"
        doc_items.fetch_from = "brand.brand_id"
        doc_items.fieldtype = "Data"
        doc_items.read_only = 1
        doc_items.length = 4
        doc_items.reqd = 0
        doc_items.insert(ignore_permissions=True)


def set_default_brand():
    gen_brand_check = frappe.db.exists('Brand', 'Generic')
    if not gen_brand_check:
        new_gen = frappe.new_doc("Brand")
        new_gen.brand = "Generic"
        new_gen.insert(ignore_permissions=True)
    doc = frappe.get_doc("Customize Form")
    doc.doc_type = "Item"
    doc.fetch_to_customize()
    for field in doc.fields:
        if field.fieldname == "brand" and field.default != "Generic":
            field.default = "Generic"
    doc.save_customization()
