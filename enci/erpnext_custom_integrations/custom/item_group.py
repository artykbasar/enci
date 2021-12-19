import frappe


def after_migrate_item_group_edit():
    extend_route_length_250()
    add_custom_fields()


def extend_route_length_250():
    doc = frappe.get_doc("Customize Form")
    doc.doc_type = "Item Group"
    doc.fetch_to_customize()
    for field in doc.fields:
        if field.fieldname == "route" and field.length != 250:
            field.length = 250
    doc.save_customization()
    

def add_custom_fields():
    item_group_id_check = frappe.db.exists('Custom Field', 'Item Group-item_group_id')
    amazon_node_id_check = frappe.db.exists('Custom Field', 'Item Group-amazon_node_id') 
    amazon_node_path_check = frappe.db.exists('Custom Field', 'Item Group-amazon_node_path')
    if not item_group_id_check:
        doc = frappe.new_doc('Custom Field')
        doc.dt = "Item Group"
        doc.label = "Item Group ID"
        doc.fieldname = "item_group_id"
        doc.insert_after = "item_group_name"
        doc.fieldtype = "Data"
        doc.length = 4
        doc.reqd = 1
        doc.unique = 1
        doc.in_list_view = 1
        doc.in_standard_filter = 1
        doc.in_global_search = 1
        doc.in_preveiw = 1
        doc.allow_in_quick_entry = 1
        doc.insert(ignore_permissions=True)
    if not amazon_node_id_check:
        doc_2 = frappe.new_doc('Custom Field')
        doc_2.dt = "Item Group"
        doc_2.label = "Amazon Node ID"
        doc_2.fieldname = "amazon_node_id"
        doc_2.insert_after = "old_parent"
        doc_2.fieldtype = "Data"
        doc_2.in_global_search = 1
        doc_2.insert(ignore_permissions=True)
    if not amazon_node_path_check:
        doc_3 = frappe.new_doc('Custom Field')
        doc_3.dt = "Item Group"
        doc_3.label = "Amazon Node Path"
        doc_3.fieldname = "amazon_node_path"
        doc_3.insert_after = "amazon_node_id"
        doc_3.length = 250
        doc_3.fieldtype = "Data"
        doc_3.translatable = 1
        doc_3.insert(ignore_permissions=True)


        