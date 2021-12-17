import frappe
from erpnext.stock.doctype.item.item import (Item, 
    strip,
    make_variant_item_code)

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

    
def after_migrate_item_edit():
    create_item_box()
    add_item_box_to_item()


def add_item_box_to_item():
    item_box_check = frappe.db.exists('DocType', 'Item Box')
    item_box_check_in_item = frappe.db.exists('Custom Field', 'Item-item_box')
    sb_item_box_check_in_item = frappe.db.exists('Custom Field', 'Item-item_box_sb')
    frappe.db.exists('Custom Field', 'Item-item_box')
    # print(item_box_check_in_item)
    if item_box_check:
        if item_box_check_in_item:
            # print('item_box feild exists in Item DocType')
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
            # print('sb_item_box feild exists in Item DocType')
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
        #print('Item Box already exist')
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
