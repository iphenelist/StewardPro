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
			"item_name": "Vifaa vya Matukio ya Vijana",
			"category": "Events",
			"department": "Idara ya Vijana",
			"description": "Vifaa vya jumla kwa matukio ya vijana na shughuli",
			"standard_cost": 500,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Nyenzo za Mafunzo ya Vijana",
			"category": "Training",
			"department": "Idara ya Vijana",
			"description": "Nyenzo za mafunzo na rasilimali kwa programu za vijana",
			"standard_cost": 300,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Vifaa vya Sauti",
			"category": "Equipment",
			"department": "Idara ya Vijana",
			"description": "Mfumo wa sauti na vifaa vya sauti kwa shughuli za vijana",
			"standard_cost": 2000,
			"unit_of_measure": "Kila"
		},

		# Music Ministry Items
		{
			"item_name": "Zana za Muziki",
			"category": "Equipment",
			"department": "Idara ya Muziki",
			"description": "Zana mbalimbali za muziki kwa ibada",
			"standard_cost": 1500,
			"unit_of_measure": "Kila"
		},
		{
			"item_name": "Muziki wa Karatasi",
			"category": "Supplies",
			"department": "Idara ya Muziki",
			"description": "Muziki wa karatasi na vitabu vya nyimbo",
			"standard_cost": 100,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Mavazi ya Kwaaya",
			"category": "Supplies",
			"department": "Idara ya Muziki",
			"description": "Mavazi ya kwaaya na vifaa vya ziada",
			"standard_cost": 800,
			"unit_of_measure": "Seti"
		},

		# Children's Ministry Items
		{
			"item_name": "Vitabu vya Watoto",
			"category": "Supplies",
			"department": "Idara ya Watoto",
			"description": "Vitabu vya elimu na kidini kwa watoto",
			"standard_cost": 200,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Vifaa vya Sanaa",
			"category": "Supplies",
			"department": "Idara ya Watoto",
			"description": "Vifaa vya sanaa na kazi ya mikono kwa shughuli za watoto",
			"standard_cost": 150,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Nyenzo za Matukio ya Watoto",
			"category": "Events",
			"department": "Idara ya Watoto",
			"description": "Nyenzo kwa matukio maalum ya watoto",
			"standard_cost": 400,
			"unit_of_measure": "Seti"
		},

		# Maintenance Items
		{
			"item_name": "Vifaa vya Usafi",
			"category": "Maintenance",
			"department": "Majengo",
			"description": "Vifaa vya usafi wa jumla na vifaa",
			"standard_cost": 300,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Zana za Ukarabati",
			"category": "Equipment",
			"department": "Majengo",
			"description": "Zana kwa matengenezo ya jengo na ukarabati",
			"standard_cost": 500,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Nyenzo za Ujenzi",
			"category": "Maintenance",
			"department": "Majengo",
			"description": "Nyenzo za ujenzi na ukarabati wa msingi",
			"standard_cost": 1000,
			"unit_of_measure": "Seti"
		},

		# Communication Items
		{
			"item_name": "Matengenezo ya Wavuti",
			"category": "Supplies",
			"department": "Mawasiliano",
			"description": "Huduma za kuandaa wavuti, kikoa, na matengenezo",
			"standard_cost": 300,
			"unit_of_measure": "Mwezi"
		},
		{
			"item_name": "Zana za Mitandao ya Kijamii",
			"category": "Supplies",
			"department": "Mawasiliano",
			"description": "Usimamizi wa mitandao ya kijamii na zana za muundo",
			"standard_cost": 150,
			"unit_of_measure": "Mwezi"
		},
		{
			"item_name": "Vifaa vya Sauti na Picha",
			"category": "Equipment",
			"department": "Mawasiliano",
			"description": "Kamera, maikrofoni, na vifaa vya kurekodi",
			"standard_cost": 2500,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Nyenzo za Uchapaji",
			"category": "Supplies",
			"department": "Mawasiliano",
			"description": "Bendera, karatasi za tangazo, habari, na nyenzo za tangazo",
			"standard_cost": 400,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Vifaa vya Utangazaji",
			"category": "Equipment",
			"department": "Mawasiliano",
			"description": "Vifaa vya kutangazia moja kwa moja na utangazaji",
			"standard_cost": 3000,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Programu ya Muundo wa Picha",
			"category": "Supplies",
			"department": "Mawasiliano",
			"description": "Leseni za programu ya muundo na usajili",
			"standard_cost": 200,
			"unit_of_measure": "Mwaka"
		},

		# General Items
		{
			"item_name": "Vifaa vya Ofisi",
			"category": "Supplies",
			"department": "Ofisi ya Wazee",
			"description": "Vifaa vya ofisi vya jumla na karatasi",
			"standard_cost": 200,
			"unit_of_measure": "Seti"
		},
		{
			"item_name": "Malipo ya Huduma za Umeme",
			"category": "Utilities",
			"department": "Ofisi ya Wazee",
			"description": "Malipo ya huduma za umeme kwa kila mwezi",
			"standard_cost": 1500,
			"unit_of_measure": "Mwezi"
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
				else:
					print(f"  ⚠ Department '{item_data['department']}' does not exist. Skipping item: {item_data['item_name']}")
					skipped_count += 1
			except Exception as e:
				print(f"  ✗ Error creating item {item_data['item_name']}: {str(e)}")
				skipped_count += 1
		else:
			skipped_count += 1
	
	frappe.db.commit()
	print(f"items creation completed! Created: {created_count}, Skipped: {skipped_count}")
