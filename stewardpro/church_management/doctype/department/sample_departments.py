# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, getdate


def create_sample_departments():
	"""Create sample departments for testing"""
	
	current_year = getdate(nowdate()).year
	
	sample_departments = [
		{
			"department_name": "Youth Ministry",
			"department_code": "YTH",
			"description": "Ministry focused on youth and young adults",
			"annual_budget": 15000.00,
			"budget_year": current_year,
			"is_active": 1
		},
		{
			"department_name": "Music Ministry",
			"department_code": "MUS",
			"description": "Worship and music ministry",
			"annual_budget": 8000.00,
			"budget_year": current_year,
			"is_active": 1
		},
		{
			"department_name": "Children Ministry",
			"department_code": "CHI",
			"description": "Ministry for children and Sunday school",
			"annual_budget": 12000.00,
			"budget_year": current_year,
			"is_active": 1
		},
		{
			"department_name": "Evangelism",
			"department_code": "EVA",
			"description": "Outreach and evangelism activities",
			"annual_budget": 20000.00,
			"budget_year": current_year,
			"is_active": 1
		},
		{
			"department_name": "Administration",
			"department_code": "ADM",
			"description": "Church administration and operations",
			"annual_budget": 25000.00,
			"budget_year": current_year,
			"is_active": 1
		},
		{
			"department_name": "Maintenance",
			"department_code": "MNT",
			"description": "Building and facility maintenance",
			"annual_budget": 18000.00,
			"budget_year": current_year,
			"is_active": 1
		},
		{
			"department_name": "Women's Ministry",
			"department_code": "WOM",
			"description": "Ministry for women's fellowship and activities",
			"annual_budget": 6000.00,
			"budget_year": current_year,
			"is_active": 1
		},
		{
			"department_name": "Men's Ministry",
			"department_code": "MEN",
			"description": "Ministry for men's fellowship and activities",
			"annual_budget": 5000.00,
			"budget_year": current_year,
			"is_active": 1
		}
	]
	
	created_departments = []
	
	for dept_data in sample_departments:
		# Check if department already exists
		existing = frappe.db.exists("Department", {"department_name": dept_data["department_name"]})
		
		if not existing:
			try:
				dept = frappe.get_doc({
					"doctype": "Department",
					**dept_data
				})
				dept.insert()
				dept.save()
				created_departments.append(dept.name)
				print(f"Created department: {dept.department_name}")
			except Exception as e:
				print(f"Error creating department {dept_data['department_name']}: {str(e)}")
		else:
			print(f"Department {dept_data['department_name']} already exists")
	
	frappe.db.commit()
	return created_departments


if __name__ == "__main__":
	create_sample_departments()
