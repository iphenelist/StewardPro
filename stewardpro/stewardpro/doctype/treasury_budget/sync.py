import frappe

TREASURY_BUDGET_DOCTYPE = "Treasury Budget"
TREASURY_BUDGET_DETAIL_DOCTYPE = "Treasury Budget Detail"
DEPARTMENT_BUDGET_DOCTYPE = "Department Budget"

@frappe.whitelist()
def handle_department_budget_change(doc, method=None):
    fiscal_year = doc.fiscal_year
    department = doc.department
    department_total_amount = doc.total_budget_amount
    department_budget_name = doc.name

    treasury_budget = frappe.get_value(
        TREASURY_BUDGET_DOCTYPE,
        {"fiscal_year": fiscal_year},
        "name"
    )

    if not treasury_budget:
        treasury_budget = frappe.get_doc({
            "doctype": TREASURY_BUDGET_DOCTYPE,
            "fiscal_year": fiscal_year,
            "details": []
        })
        treasury_budget.insert(ignore_permissions=True)
    else:
        treasury_budget = frappe.get_doc(TREASURY_BUDGET_DOCTYPE, treasury_budget)

    # Find or create detail row for department
    found = False
    for row in treasury_budget.details:
        if row.department == department:
            row.department_total_amount = department_total_amount
            row.department_budget = department_budget_name
            found = True
            break
    if not found:
        treasury_budget.append("details", {
            "department": department,
            "department_total_amount": department_total_amount,
            "department_budget": department_budget_name
        })

    treasury_budget.total_amount = sum([d.department_total_amount or 0 for d in treasury_budget.details])
    treasury_budget.save(ignore_permissions=True)

def handle_department_budget_delete(doc, method=None):
    fiscal_year = doc.fiscal_year
    department = doc.department

    treasury_budget_name = frappe.get_value(
        TREASURY_BUDGET_DOCTYPE,
        {"fiscal_year": fiscal_year},
        "name"
    )
    if not treasury_budget_name:
        return

    treasury_budget = frappe.get_doc(TREASURY_BUDGET_DOCTYPE, treasury_budget_name)
    treasury_budget.details = [
        d for d in treasury_budget.details if d.department != department
    ]
    treasury_budget.total_amount = sum([d.department_total_amount or 0 for d in treasury_budget.details])
    treasury_budget.save(ignore_permissions=True)

def rebuild_treasury_for_year(fiscal_year):
    treasury_budget = frappe.get_value(
        TREASURY_BUDGET_DOCTYPE,
        {"fiscal_year": fiscal_year},
        "name"
    )
    if treasury_budget:
        treasury_budget = frappe.get_doc(TREASURY_BUDGET_DOCTYPE, treasury_budget)
        treasury_budget.details = []
    else:
        treasury_budget = frappe.get_doc({
            "doctype": TREASURY_BUDGET_DOCTYPE,
            "fiscal_year": fiscal_year,
            "details": []
        })

    department_budgets = frappe.get_all(
        DEPARTMENT_BUDGET_DOCTYPE,
        filters={"fiscal_year": fiscal_year},
        fields=["name", "department", "total_budget_amount"]
    )

    for db in department_budgets:
        treasury_budget.append("details", {
            "department": db["department"],
            "department_total_amount": db["total_budget_amount"],
            "department_budget": db["name"]
        })

    treasury_budget.total_amount = sum([d.department_total_amount or 0 for d in treasury_budget.details])
    treasury_budget.save(ignore_permissions=True)
    return treasury_budget.name
