# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe

def execute():
	"""Create sample items for different departments - runs after installation"""
	
	print("Creating sample items...")
	
	# Sample items data
	sample_items = [
		# Youth Ministry Items
		{
			"item_name": "Youth Event Supplies",
			"category": "Events",
			"department": "Youth Ministry",
			"description": "General supplies for youth events and activities",
			"standard_cost": 500,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Youth Training Materials",
			"category": "Training",
			"department": "Youth Ministry", 
			"description": "Training materials and resources for youth programs",
			"standard_cost": 300,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Sound Equipment",
			"category": "Equipment",
			"department": "Youth Ministry",
			"description": "Sound system and audio equipment for youth activities",
			"standard_cost": 2000,
			"unit_of_measure": "Each"
		},
		
		# Music Ministry Items
		{
			"item_name": "Musical Instruments",
			"category": "Equipment",
			"department": "Music Ministry",
			"description": "Various musical instruments for worship",
			"standard_cost": 1500,
			"unit_of_measure": "Each"
		},
		{
			"item_name": "Sheet Music",
			"category": "Supplies",
			"department": "Music Ministry",
			"description": "Sheet music and songbooks",
			"standard_cost": 100,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Choir Robes",
			"category": "Supplies",
			"department": "Music Ministry",
			"description": "Choir robes and accessories",
			"standard_cost": 800,
			"unit_of_measure": "Set"
		},
		
		# Children's Ministry Items
		{
			"item_name": "Children's Books",
			"category": "Supplies",
			"department": "Children's Ministry",
			"description": "Educational and religious books for children",
			"standard_cost": 200,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Craft Supplies",
			"category": "Supplies",
			"department": "Children's Ministry",
			"description": "Art and craft supplies for children's activities",
			"standard_cost": 150,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Children's Event Materials",
			"category": "Events",
			"department": "Children's Ministry",
			"description": "Materials for children's special events",
			"standard_cost": 400,
			"unit_of_measure": "Set"
		},
		
		# Maintenance Items
		{
			"item_name": "Cleaning Supplies",
			"category": "Maintenance",
			"department": "Maintenance",
			"description": "General cleaning supplies and equipment",
			"standard_cost": 300,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Repair Tools",
			"category": "Equipment",
			"department": "Maintenance",
			"description": "Tools for building maintenance and repairs",
			"standard_cost": 500,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Building Materials",
			"category": "Maintenance",
			"department": "Maintenance",
			"description": "Basic building and repair materials",
			"standard_cost": 1000,
			"unit_of_measure": "Set"
		},
		
		# Communication Items
		{
			"item_name": "Website Maintenance",
			"category": "Supplies",
			"department": "Communication",
			"description": "Website hosting, domain, and maintenance services",
			"standard_cost": 300,
			"unit_of_measure": "Month"
		},
		{
			"item_name": "Social Media Tools",
			"category": "Supplies",
			"department": "Communication",
			"description": "Social media management and design tools subscriptions",
			"standard_cost": 150,
			"unit_of_measure": "Month"
		},
		{
			"item_name": "Audio Visual Equipment",
			"category": "Equipment",
			"department": "Communication",
			"description": "Cameras, microphones, and recording equipment",
			"standard_cost": 2500,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Printing Materials",
			"category": "Supplies",
			"department": "Communication",
			"description": "Banners, flyers, bulletins, and promotional materials",
			"standard_cost": 400,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Broadcasting Equipment",
			"category": "Equipment",
			"department": "Communication",
			"description": "Live streaming and broadcasting equipment",
			"standard_cost": 3000,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Graphic Design Software",
			"category": "Supplies",
			"department": "Communication",
			"description": "Design software licenses and subscriptions",
			"standard_cost": 200,
			"unit_of_measure": "Year"
		},

		# General Items
		{
			"item_name": "Office Supplies",
			"category": "Supplies",
			"department": "General",
			"description": "General office supplies and stationery",
			"standard_cost": 200,
			"unit_of_measure": "Set"
		},
		{
			"item_name": "Utilities Payment",
			"category": "Utilities",
			"department": "General",
			"description": "Monthly utilities payment",
			"standard_cost": 1500,
			"unit_of_measure": "Month"
		}
	]
	
	created_count = 0
	skipped_count = 0
	
	for item_data in sample_items:
		# Check if item already exists
		if not frappe.db.exists("Item", item_data["item_name"]):
			try:
				# Check if department exists
				if frappe.db.exists("Department", item_data["department"]):
					item_doc = frappe.get_doc({
						"doctype": "Item",
						**item_data,
						"is_active": 1
					})
					item_doc.insert(ignore_permissions=True)
					created_count += 1
					print(f"  ✓ Created item: {item_data['item_name']}")
				else:
					print(f"  ⚠ Department '{item_data['department']}' does not exist. Skipping item: {item_data['item_name']}")
					skipped_count += 1
			except Exception as e:
				print(f"  ✗ Error creating item {item_data['item_name']}: {str(e)}")
				skipped_count += 1
		else:
			print(f"  ℹ Item already exists: {item_data['item_name']}")
			skipped_count += 1
	
	frappe.db.commit()
	print(f"Sample items creation completed! Created: {created_count}, Skipped: {skipped_count}")
