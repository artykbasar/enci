import frappe
from frappe.core.doctype.file.file import (File, MaxFileSizeReachedError, _, cint, conf)



class ENCIFile(File):
    def check_max_file_size(self):
        max_file_size = get_max_file_size()
        file_size = len(self.content)

        if file_size > max_file_size:
            frappe.msgprint(_("File size exceeded the maximum allowed size of {0} MB").format(
				max_file_size / 1048576),
				raise_exception=MaxFileSizeReachedError)

        return file_size


def get_max_file_size():
	return cint(conf.get('max_file_size')) or (10485760*5)

def extend_file_name_length_250():
    doc = frappe.get_doc("Customize Form")
    doc.doc_type = "File"
    doc.fetch_to_customize()
    for field in doc.fields:
        if field.fieldname == "file_name" and field.length != 250:
            field.length = 250
    doc.save_customization()

def after_migrate_file_edit():
    extend_file_name_length_250()

