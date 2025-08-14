import frappe
from datetime import date

def create_fiscal_year():
    current_year = date.today().year
    next_year = current_year + 1
    fiscal_year_name = f"{current_year}-{str(next_year)[-2:]}"
    start_date = date(current_year, 1, 1)
    end_date = date(next_year, 12, 31)
    if not frappe.db.exists("Fiscal Year", fiscal_year_name):
        doc = frappe.get_doc({
            "doctype": "Fiscal Year",
            "year": fiscal_year_name,
            "year_start_date": start_date,
            "year_end_date": end_date,
            "is_short_year": 0,
            "disabled": 0,
            "auto_created": 0
        })
        doc.insert(ignore_permissions=True)
        print(f"Fiscal Year created: {fiscal_year_name}")
    else:
        print(f"Fiscal Year already exists: {fiscal_year_name}")

if __name__ == "__main__":
    create_fiscal_year()
