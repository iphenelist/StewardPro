# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

def execute():
	"""Migrate Department Expense from single fields to child table structure"""
	
	print("Starting Department Expense migration to child table structure...")
	
	# Get all existing Department Expense records
	expenses = frappe.get_all(
		"Department Expense",
		fields=[
			"name", "item", "expense_category", "expense_description", 
			"amount", "department", "docstatus"
		],
		filters={"docstatus": ["!=", 2]}  # Exclude cancelled documents
	)
	
	migrated_count = 0
	skipped_count = 0
	error_count = 0
	
	for expense_data in expenses:
		try:
			# Get the full document
			expense_doc = frappe.get_doc("Department Expense", expense_data.name)
			
			# Check if already migrated (has expense_details)
			if expense_doc.get("expense_details"):
				print(f"Skipping {expense_data.name} - already has expense details")
				skipped_count += 1
				continue
			
			# Create expense detail from old fields
			if expense_data.get("expense_description") and expense_data.get("amount"):
				expense_detail = {
					"item": expense_data.get("item"),
					"expense_category": expense_data.get("expense_category") or "Other",
					"expense_description": expense_data.get("expense_description"),
					"quantity": 1.0,  # Default quantity
					"unit_price": expense_data.get("amount"),
					"amount": expense_data.get("amount")
				}
				
				# Add the detail to the document
				expense_doc.append("expense_details", expense_detail)
				
				# Set total amount
				expense_doc.total_amount = expense_data.get("amount")
				
				# Save without validation to avoid issues during migration
				expense_doc.flags.ignore_validate = True
				expense_doc.flags.ignore_mandatory = True
				expense_doc.save()
				
				print(f"Migrated {expense_data.name}: {expense_data.expense_description} - ${expense_data.amount}")
				migrated_count += 1
			else:
				print(f"Skipping {expense_data.name} - missing required data")
				skipped_count += 1
				
		except Exception as e:
			print(f"Error migrating {expense_data.name}: {str(e)}")
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
