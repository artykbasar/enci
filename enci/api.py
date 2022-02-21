from __future__ import unicode_literals
import frappe
import json
from frappe.utils import floor, flt, today, cint
from frappe import _, throw
from frappe.exceptions import DuplicateEntryError
from frappe.core.page.background_jobs.background_jobs import get_info


def publish_progress(docname, id, achieved, total, description, field_name=None, done_message="Done", title="Loading", reload=False):
    frappe.publish_realtime(id, 
                            {
                                "title": title, 
                                "count": achieved, 
                                "total": total,
                                "percentage": achieved / total * 100, 
                                "description": f"Progress: {achieved}/{total} {description}", 
                                "reload": reload,
                                "fieldname": field_name,
                                "done_message": done_message
                            }, 
                            user=frappe.session.user, 
                            after_commit=False,
                            docname=docname)

def backgroud_jobs_check(function_path):
    list_of_jobs = get_info()
    if list_of_jobs:
        for job in list_of_jobs:
            if job['job_name'] == function_path:
                throw(_([f"Current Job Status: {job['status']}", 
                        f"Job has been created at: {job['creation']}"]), 
                    DuplicateEntryError, 
                    "This job already in progress", 
                    as_list=True)


def whitelabel_patch():
	#delete erpnext welcome page 
	frappe.delete_doc_if_exists('Page', 'welcome-to-erpnext', force=1)
	#update Welcome Blog Post
	if frappe.db.exists("Blog Post", "Welcome"):
		frappe.db.set_value("Blog Post","Welcome","content","")
	update_field_label()
	if cint(get_frappe_version()) >= 13 and not frappe.db.get_single_value('Whitelabel Setting', 'ignore_onboard_whitelabel'):
		update_onboard_details()
	change_app_name_to_company_name()


def change_app_name_to_company_name():
	doc = frappe.get_doc("Website Settings")
	company_name = frappe.get_doc("Global Defaults")
	save_trigger = False
	if doc.app_name != company_name.default_company:
		doc.app_name = company_name.default_company
		save_trigger = True
	if doc.app_logo != "/assets/enci/images/home.png":
		doc.app_logo = '/assets/enci/images/home.png'
		save_trigger = True
	if save_trigger:
		doc.save(ignore_permissions=True)



def update_field_label():
	"""Update label of section break in employee doctype"""
	frappe.db.sql("""Update `tabDocField` set label='ERP' where fieldname='erpnext_user' and parent='Employee'""")

def get_frappe_version():
	return frappe.db.get_value("Installed Application",{"app_name":"frappe"},"app_version").split('.')[0]

def update_onboard_details():
	update_onboard_module()
	update_onborad_steps()

def update_onboard_module():
	onboard_module_details = frappe.get_all("Module Onboarding",filters={},fields=["name"])
	for row in onboard_module_details:
		doc = frappe.get_doc("Module Onboarding",row.name)
		doc.documentation_url = ""
		doc.flags.ignore_mandatory = True
		doc.save(ignore_permissions = True)

def update_onborad_steps():
	onboard_steps_details = frappe.get_all("Onboarding Step",filters={},fields=["name"])
	for row in onboard_steps_details:
		doc = frappe.get_doc("Onboarding Step",row.name)
		doc.intro_video_url = ""
		doc.description = ""
		doc.flags.ignore_mandatory = True
		doc.save(ignore_permissions = True)

def boot_session(bootinfo):
	"""boot session - send website info if guest"""
	if frappe.session['user']!='Guest':

		bootinfo.whitelabel_setting = frappe.get_doc("Whitelabel Setting","Whitelabel Setting")

@frappe.whitelist()
def ignore_update_popup():
	if not frappe.db.get_single_value('Whitelabel Setting', 'disable_new_update_popup'):
		show_update_popup_update()

@frappe.whitelist()
def show_update_popup_update():
	cache = frappe.cache()
	user  = frappe.session.user
	update_info = cache.get_value("update-info")
	if not update_info:
		return

	updates = json.loads(update_info)

	# Check if user is int the set of users to send update message to
	update_message = ""
	if cache.sismember("update-user-set", user):
		for update_type in updates:
			release_links = ""
			for app in updates[update_type]:
				app = frappe._dict(app)
				release_links += "<b>{title}</b>: <a href='https://github.com/{org_name}/{app_name}/releases/tag/v{available_version}'>v{available_version}</a><br>".format(
					available_version = app.available_version,
					org_name          = app.org_name,
					app_name          = app.app_name,
					title             = app.title
				)
			if release_links:
				message = _("New {} releases for the following apps are available").format(_(update_type))
				update_message += "<div class='new-version-log'>{0}<div class='new-version-links'>{1}</div></div>".format(message, release_links)

	if update_message:
		frappe.msgprint(update_message, title=_("New updates are available"), indicator='green')
		cache.srem("update-user-set", user)
