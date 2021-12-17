import frappe
from frappe import _, throw, msgprint
from frappe.utils import cint
from frappe.utils import now_datetime
from frappe.model.naming import getseries
from erpnext.setup.doctype.naming_series.naming_series import NamingSeries


class ENCINamingSeries(NamingSeries):

	def validate_series_name(self, n):
		import re
		if not re.match("^[\w\- /.#{}\[\]]*$", n, re.UNICODE):
			throw(_('Special Characters except "-", "#", ".", "/", "{", "}", "[" and "]" not allowed in naming series'))
	@frappe.whitelist()
	def get_current(self, arg=None):
		"""get series current"""
		if self.prefix:
			prefix = self.parse_naming_series()
			self.current_value = frappe.db.get_value("Series",
				prefix, "current", order_by = "name")
	
	@frappe.whitelist()
	def update_series_start(self):
		if self.prefix:
			prefix = self.parse_naming_series()
			self.insert_series(prefix)
			frappe.db.sql("update `tabSeries` set current = %s where name = %s",
				(cint(self.current_value), prefix))
			msgprint(_("Series Updated Successfully"))
		else:
			msgprint(_("Please select prefix first"))

	def parse_naming_series(self):
		parts = self.prefix.split('.')

		# Remove ### from the end of series
		if parts[-1] == "#" * len(parts[-1]):
			del parts[-1]
        
		prefix = parse_naming_series(parts)
		return prefix

def set_name_by_naming_series(doc):
	"""Sets name by the `naming_series` property"""
	if not doc.naming_series:
		doc.naming_series = get_default_naming_series(doc.doctype)

	if not doc.naming_series:
		frappe.throw(frappe._("Naming Series mandatory"))

	doc.name = make_autoname(doc.naming_series+".#####", "", doc)


def make_autoname(key="", doctype="", doc=""):
	"""
	Creates an autoname from the given key:

	**Autoname rules:**

		 * The key is separated by '.'
		 * '####' represents a series. The string before this part becomes the prefix:
			Example: ABC.#### creates a series ABC0001, ABC0002 etc
		 * 'MM' represents the current month
		 * 'YY' and 'YYYY' represent the current year


   *Example:*

		 * DE/./.YY./.MM./.##### will create a series like
		   DE/09/01/0001 where 09 is the year, 01 is the month and 0001 is the series
	"""
	if key == "hash":
		return frappe.generate_hash(doctype, 10)

	if "#" not in key:
		key = key + ".#####"
	elif "." not in key:
		error_message = _("Invalid naming series (. missing)")
		if doctype:
			error_message = _("Invalid naming series (. missing) for {0}").format(doctype)

		frappe.throw(error_message)

	parts = key.split('.')
	n = parse_naming_series(parts, doctype, doc)
	return n


def parse_naming_series(parts, doctype='', doc=''):
	n = ''
	if isinstance(parts, str):
		parts = parts.split('.')
	series_set = False
	hash_ = False
	today = now_datetime()
	for e in parts:
		part = ''
		if e.startswith('#'):
			if not series_set:
				if "[hash]" in e.lower():
					e = e.split("[")[0]
					hash_ = True
				digits = len(e)
				part = getseries(n, digits)
				if hash_:
					part = frappe.generate_hash(doctype + part, digits).upper()
				series_set = True
		elif e == 'YY':
			part = today.strftime('%y')
		elif e == 'MM':
			part = today.strftime('%m')
		elif e == 'DD':
			part = today.strftime("%d")
		elif e == 'YYYY':
			part = today.strftime('%Y')
		elif e == 'timestamp':
			part = str(today)
		elif e == 'FY':
			part = frappe.defaults.get_user_default("fiscal_year")
		elif e.startswith('{') and doc:
			e = e.replace('{', '').replace('}', '')
			part = doc.get(e)
		elif doc and doc.get(e):
			part = doc.get(e)
		else:
			part = e

		if isinstance(part, str):
			n += part

	return n


def get_default_naming_series(doctype):
	"""get default value for `naming_series` property"""
	naming_series = frappe.get_meta(doctype).get_field("naming_series").options or ""
	if naming_series:
		naming_series = naming_series.split("\n")
		return naming_series[0] or naming_series[1]
	else:
		return None