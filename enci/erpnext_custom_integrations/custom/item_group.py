# %%
import frappe
import pandas as pd
from frappe.utils import (cint, now)


pd.set_option('expand_frame_repr', False)
pd.set_option('display.min_rows', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


def after_migrate_item_group_edit():
    if cint(frappe.db.get_single_value("System Settings", "setup_complete") or 0):
        extend_route_length_250()
        add_custom_fields()


def add_item_group_values_from_csv(doc):
    if not cint(doc.item_group_presets or 0):
        after_migrate_item_group_edit()
        df = pd.read_csv("assets/enci/tabItem_Group.csv")
        ig_doc = frappe.get_all("Item Group", fields=["name", "lft", "rgt"], order_by="lft")
        main_ig = ig_doc[0]
        add_n = main_ig['rgt'] - main_ig['lft']
        main_ig_rgt = df.loc[df["lft"] == 1]['rgt'].iloc[0] + add_n + 1
        df.loc[df["lft"] == 1, ["parent", "parent_item_group", "old_parent"]] = main_ig["name"]
        df['rgt'] = df['rgt'] + add_n
        df['lft'] = df['lft'] + add_n
        df.sort_values(by="lft", inplace=True)
        df.reset_index(inplace=True, drop=True)
        progress_total = len(df)
        for index, row in df.iterrows():
            existance_check = frappe.db.exists('Item Group', row['name'])
            if not existance_check:
                time_stamp = now()
                sql_query = f"""
                                INSERT INTO `tabItem Group` (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `parent`, `parentfield`, `parenttype`, `idx`, `item_group_name`, `parent_item_group`, `is_group`, `image`, `show_in_website`, `route`, `weightage`, `slideshow`, `website_title`, `description`, `lft`, `rgt`, `old_parent`, `_user_tags`, `_comments`, `_assign`, `_liked_by`, `item_group_id`, `amazon_node_id`, `amazon_node_path`) VALUES
                                ("{row['name']}", "{time_stamp}", "{time_stamp}", 'Administrator', 'Administrator', {row["docstatus"]}, NULL, NULL, NULL, {row["idx"]}, "{row["item_group_name"]}", "{row["parent_item_group"]}", {row["is_group"]}, NULL, {row["show_in_website"]}, "{row["route"]}", {row["weightage"]}, NULL, "{row["website_title"]}", NULL, {row["lft"]}, {row["rgt"]}, "{row["old_parent"]}", NULL, NULL, NULL, NULL, "{row["item_group_id"]}", "{row["amazon_node_id"]}", "{row["amazon_node_path"]}");
                            """
                uploaded = True
                while uploaded:
                    try:
                        frappe.db.sql(sql_query, ignore_ddl=True)
                        uploaded = False
                    except Exception as e:
                        publish_progress(index+1, progress_total, f"Queary Progeress {index+1}/{progress_total} {row['name']} \n {e}")
                        uploaded = False
                publish_progress(index+1, progress_total, f"Queary Progeress {index+1}/{progress_total} {row['name']} \n Has been added to DB")
            else:
                publish_progress(index+1, progress_total, f"Queary Progeress {index+1}/{progress_total} {row['name']} \n already exists in DB")
        doc.item_group_presets = 1
        doc.save()


def add_item_group_values_from_sql(doc):
    if not cint(doc.item_group_presets or 0):
        with open('assets/enci/tabItem_Group.sql') as f:
            contents = f.read()
        contents = contents.split(';')
        progress_total = len(contents)

        for index, each in enumerate(contents):
            if each.strip():
                frappe.db.sql(each+";", ignore_ddl=True)
            publish_progress(index+1, progress_total, f"Queary Progeress {index+1}/{progress_total}")
        doc.item_group_presets = 1
        doc.save()
    else:
        print("already has been loaded")


def publish_progress(achieved, total, description, reload=False):
    frappe.publish_realtime("sql_import_progress", 
                            {
                                "title": "Loading", 
                                "count": achieved, 
                                "total": total,
                                "percentage": achieved / total * 100, 
                                "description": description, 
                                "reload": reload
                            }, 
                            user=frappe.session.user, 
                            after_commit=False,
                            docname="ENCI Settings")



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

