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

