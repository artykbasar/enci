import frappe
from frappe import (throw, _, msgprint)
from frappe.exceptions import DuplicateEntryError
from frappe.core.page.background_jobs.background_jobs import get_info
__version__ = '0.0.1'


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
        

