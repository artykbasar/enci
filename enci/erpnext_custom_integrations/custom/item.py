from bs4.builder import TreeBuilder
import frappe
from erpnext.stock.doctype.item.item import (Item, 
    strip,
    make_variant_item_code)
from frappe.utils import cint


class ENCIItem(Item):
    def autoname(self):
        if frappe.db.get_default("item_naming_by") == "Naming Series":
            if self.variant_of:
                if not self.item_code:
                    template_item_name = frappe.db.get_value("Item", self.variant_of, "item_name")
                    make_variant_item_code(self.variant_of, template_item_name, self)
            else:
                from enci.erpnext_custom_integrations.custom.naming_series import set_name_by_naming_series
                set_name_by_naming_series(self)
                self.item_code = self.name

        self.item_code = strip(self.item_code)
        self.name = self.item_code
    
    def validate(self):
        org_validate = super(ENCIItem, self).validate()
        self.full_item_code = f"{self.brand_id}{self.item_group_id}{self.item_code}"
        return org_validate

    def on_trash(self):
        self.unlink_f2g_on_delete()
        return super(ENCIItem, self).on_trash()
    
    def unlink_f2g_on_delete(self):
        f2g_check = frappe.db.get_list("Furniture To Go Products", 
                        filters={'item': self.name}, fields=['name'])
        if f2g_check:
            for each in f2g_check:
                frappe.db.set_value("Furniture To Go Products", each['name'], {'item': ''})

    
def after_migrate_item_edit():
    create_item_box()
    add_item_box_to_item()
    set_item_code_to_naming_series()
    set_item_code_format()
    add_full_item_code()
    if cint(frappe.db.get_single_value("System Settings", "setup_complete") or 0):
        set_stock_settings_defaults()


def add_full_item_code():
    full_item_item_code_check = frappe.db.exists('Custom Field', 'Item-full_item_code')
    if not full_item_item_code_check:
        doc = frappe.new_doc('Custom Field')
        doc.dt = 'Item'
        doc.label = 'Full Item Code'
        doc.fieldname = 'full_item_code'
        doc.insert_after = 'item_group_id'
        doc.fieldtype = 'Read Only'
        doc.unique = 1
        doc.in_list_view = 1
        doc.in_standard_filter = 1
        doc.in_global_search = 1
        doc.in_preveiw = 1
        doc.insert(ignore_permissions=True)


def set_stock_settings_defaults():
    doc = frappe.get_doc("Stock Settings")
    save_trigger = False
    # Setting Item Group Default value
    if not doc.item_group:
        products_0002_check = frappe.db.exists('Item Group', 'Products - 0002')
        if products_0002_check:
            doc.item_group = "Products - 0002"
            save_trigger = True
        else:
            products_check = frappe.db.exists('Item Group', 'Products')
            if products_check:
                doc.item_group = "Products"
                save_trigger = True
    # Setting Stock UOM Default value
    if not doc.stock_uom or doc.stock_uom == "Nos":
        uom_doc = frappe.get_doc("UOM", "Unit")
        uom_save_trigger = False
        if uom_doc.enabled != 1:
            uom_doc.enabled = 1
            uom_save_trigger = True
        if uom_doc.must_be_whole_number != 1:
            uom_doc.must_be_whole_number = 1
            uom_save_trigger = True
        if uom_save_trigger:
            uom_doc.save(ignore_permissions=True)
        doc.stock_uom = "Unit"
        save_trigger = True
    # Setting Allow Negative Stock to True
    if not doc.allow_negative_stock:
        doc.allow_negative_stock = 1
        save_trigger = True
    # Setting Barcode Section as visiable  
    if not doc.show_barcode_field:
        doc.show_barcode_field = 1
        save_trigger = True
    if save_trigger:
        doc.save(ignore_permissions=True)


def set_item_code_format():
    doc = frappe.get_doc("Naming Series")
    doc.select_doc_for_series = "Item"
    if doc.get_options() != ".#######[Hash]":
        doc.set_options = ".#######[Hash]"
        doc.update_series()


def set_item_code_to_naming_series():
    doc = frappe.get_doc("Stock Settings")
    if doc.item_naming_by != "Naming Series":
        doc.item_naming_by = "Naming Series"
        doc.save(ignore_permissions=True)


def add_item_box_to_item():
    item_box_check = frappe.db.exists('DocType', 'Item Box')
    item_box_check_in_item = frappe.db.exists('Custom Field', 'Item-item_box')
    sb_item_box_check_in_item = frappe.db.exists('Custom Field', 'Item-item_box_sb')
    frappe.db.exists('Custom Field', 'Item-item_box')
    if item_box_check:
        if item_box_check_in_item:
            pass
        else:
            doc = frappe.new_doc('Custom Field')
            doc.dt = 'Item'
            doc.label = 'Item Box '
            doc.fieldname = 'item_box'
            doc.insert_after = 'description'
            doc.fieldtype = 'Table'
            doc.options = 'Item Box'
            doc.insert(ignore_permissions=True)
        if sb_item_box_check_in_item:
            pass
        else:
            doc_2 = frappe.new_doc('Custom Field')
            doc_2.dt = 'Item'
            doc_2.label = 'Item Box sb'
            doc_2.fieldname = 'item_box_sb'
            doc_2.insert_after = 'description'
            doc_2.fieldtype = 'Section Break'
            doc_2.insert(ignore_permissions=True)
    else:
        print('Item Box Doctype has not been created, Please Create it Fist')


def create_item_box():
    item_box_check = frappe.db.exists('DocType', 'Item Box')
    if item_box_check:
        pass
    else:
        doc = frappe.new_doc('DocType')
        doc.name = 'Item Box'
        doc.module = 'Stock'
        doc.istable = 1
        doc.editable_grid = 1
        doc.track_views = 1
        doc.custom = 1
        doc.append('fields', 
                {"label":"Box Number",
                "fieldtype": "Data",
                'fieldname': 'box_number',
                'in_list_view': 1,
                'columns': 1
            })
        doc.append('fields',
                {"label": "EAN",
                "fieldtype": "Barcode",
                'fieldname': 'box_ean',
                'in_list_view': 1,
                'columns': 2
            })
        doc.append('fields',
                {"label": "UPC",
                "fieldtype": "Barcode",
                'fieldname': 'box_upc',
                'in_list_view': 1,
                'columns': 2
            })
        doc.append('fields',
                {"label": "Height",
                "fieldtype": "Float",
                'precision': 1,
               'fieldname': 'box_height',
                'in_list_view': 1,
                'columns': 1
            })
        doc.append('fields',
                {"label": "Width",
                "fieldtype": "Float",
                'precision': 1,
                'fieldname': 'box_width',
                'in_list_view': 1,
                'columns': 1
            })
        doc.append('fields',
                {"label": "Depth",
                "fieldtype": "Float",
                'precision': 1,
                'fieldname': 'box_depth',
                'in_list_view': 1,
                'columns': 1
            })
        doc.append('fields',
                {"label": "Unit",
                "fieldtype": "Data",
                'fieldname': 'box_dim_unit',
                'in_list_view': 1,
                'columns': 1
            })
        doc.append('fields',
                {"label": "Weight",
                "fieldtype": "Float",
                'precision': 3,
                'fieldname': 'box_weight',
                'in_list_view': 1,
                'columns': 1
            })
        doc.document_type = 'Document'
        doc.insert(ignore_permissions=True)
