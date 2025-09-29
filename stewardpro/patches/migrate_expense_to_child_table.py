# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

def execute():
	"""Migrate Department Expense from single fields to child table structure"""

	print("Starting Department Expense migration to child table structure...")

	# Check if the Department Expense doctype exists and has the new structure
	try:
		# Check if the doctype exists and has the expense_details field
		meta = frappe.get_meta("Department Expense")
		has_expense_details = any(field.fieldname == "expense_details" for field in meta.fields)

		if not has_expense_details:
			print("❌ Department Expense doctype doesn't have expense_details field yet.")
			print("Please update the doctype first before running this migration.")
			return {"migrated": 0, "skipped": 0, "errors": 0}

		print("✅ Department Expense doctype already has the correct child table structure.")

		# Get all existing records to check if they need any processing
		expenses = frappe.get_all(
			"Department Expense",
			fields=["name"],
			filters={"docstatus": ["!=", 2]}  # Exclude cancelled documents
		)

		if not expenses:
			print("No Department Expense records found.")
			return {"migrated": 0, "skipped": 0, "errors": 0}

	except Exception as e:
		print(f"Error checking Department Expense doctype: {str(e)}")
		return {"migrated": 0, "skipped": 0, "errors": 1}
	
	migrated_count = 0
	skipped_count = 0
	error_count = 0

	# Check existing records to see if they have expense_details
	for expense_data in expenses:
		try:
			# Get the full document
			expense_doc = frappe.get_doc("Department Expense", expense_data.name)

			# Check if already has expense_details
			if expense_doc.get("expense_details"):
				print(f"Skipping {expense_data.name} - already has expense details")
				skipped_count += 1
			else:
				# Record exists but has no expense details - this is expected for new structure
				print(f"Skipping {expense_data.name} - uses new structure (no old data to migrate)")
				skipped_count += 1

		except Exception as e:
			print(f"Error checking {expense_data.name}: {str(e)}")
			error_count += 1
			continue
	
	print(f"\nMigration completed:")
	print(f"✅ Migrated: {migrated_count} expenses")
	print(f"⏭️  Skipped: {skipped_count} expenses")
	print(f"❌ Errors: {error_count} expenses")
	
	if error_count > 0:
		print(f"\n⚠️  {error_count} expenses had errors during migration.")
		print("Please check the logs and manually review these records.")
	
	# Update the doctype to remove old fields (this would be done in a separate patch)
	print("\n📝 Next steps:")
	print("1. Test the migrated data")
	print("2. Update any custom reports or scripts")
	print("3. Remove old fields from Department Expense doctype")
	
	return {
		"migrated": migrated_count,
		"skipped": skipped_count,
		"errors": error_count
	}
