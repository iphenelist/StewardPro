import frappe


def after_install():
	create_roles()
	create_default_departments()
	create_default_positions()
	create_default_offering_types()


def create_roles():
	roles = [
		"Pastor",
		"Church Elder",
		"Church Clerk",
		"Treasurer",
		"SS Superintendent",
		"SS Teacher",
		"Deacon",
		"Church Member",
	]
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)


def create_default_departments():
	departments = [
		{"department_name": "Adventist Youth", "abbreviation": "AY", "department_type": "Ministry"},
		{"department_name": "Dorcas / Community Services", "abbreviation": "ACS", "department_type": "Service"},
		{"department_name": "Personal Ministries", "abbreviation": "PM", "department_type": "Ministry"},
		{"department_name": "Health Ministries", "abbreviation": "HM", "department_type": "Ministry"},
		{"department_name": "Music Ministry", "abbreviation": "MM", "department_type": "Ministry"},
		{"department_name": "Sabbath School", "abbreviation": "SS", "department_type": "Ministry"},
		{"department_name": "Deacons Ministry", "abbreviation": "DM", "department_type": "Service"},
		{"department_name": "Deaconesses Ministry", "abbreviation": "DSM", "department_type": "Service"},
		{"department_name": "Children's Ministries", "abbreviation": "CM", "department_type": "Ministry"},
		{"department_name": "Family Ministries", "abbreviation": "FM", "department_type": "Ministry"},
		{"department_name": "Communication", "abbreviation": "COM", "department_type": "Support"},
		{"department_name": "Education", "abbreviation": "EDU", "department_type": "Ministry"},
		{"department_name": "Stewardship", "abbreviation": "STW", "department_type": "Ministry"},
		{"department_name": "Women's Ministries", "abbreviation": "WM", "department_type": "Ministry"},
		{"department_name": "Men's Ministries", "abbreviation": "MEN", "department_type": "Ministry"},
		{"department_name": "Prayer Ministries", "abbreviation": "PRM", "department_type": "Ministry"},
		{"department_name": "Publishing Ministries", "abbreviation": "PUB", "department_type": "Ministry"},
	]
	for dept in departments:
		if not frappe.db.exists("Church Department", {"department_name": dept["department_name"]}):
			doc = frappe.get_doc({"doctype": "Church Department", "enabled": 1, **dept})
			doc.insert(ignore_permissions=True)


def create_default_positions():
	positions = [
		{"position_name": "Pastor", "position_category": "Leadership"},
		{"position_name": "Head Elder", "position_category": "Leadership"},
		{"position_name": "Elder", "position_category": "Leadership"},
		{"position_name": "Church Clerk", "position_category": "Officer"},
		{"position_name": "Treasurer", "position_category": "Officer"},
		{"position_name": "Head Deacon", "position_category": "Officer"},
		{"position_name": "Head Deaconess", "position_category": "Officer"},
		{"position_name": "Deacon", "position_category": "Officer"},
		{"position_name": "Deaconess", "position_category": "Officer"},
		{"position_name": "Sabbath School Superintendent", "position_category": "Departmental Leader"},
		{"position_name": "AY Leader", "position_category": "Departmental Leader"},
		{"position_name": "Personal Ministries Leader", "position_category": "Departmental Leader"},
		{"position_name": "Dorcas Leader", "position_category": "Departmental Leader"},
		{"position_name": "Health Ministries Leader", "position_category": "Departmental Leader"},
		{"position_name": "Music Director", "position_category": "Departmental Leader"},
		{"position_name": "Communication Secretary", "position_category": "Departmental Leader"},
		{"position_name": "Church Board Member", "position_category": "Board Member"},
	]
	for pos in positions:
		if not frappe.db.exists("Church Position", {"position_name": pos["position_name"]}):
			doc = frappe.get_doc({"doctype": "Church Position", "enabled": 1, **pos})
			doc.insert(ignore_permissions=True)


def create_default_offering_types():
	offering_types = [
		{"offering_name": "Tithe", "offering_category": "Tithe", "is_remittable": 1},
		{"offering_name": "Church Budget", "offering_category": "Regular Offering", "is_remittable": 0},
		{"offering_name": "Sabbath School Offering", "offering_category": "Regular Offering", "is_remittable": 1},
		{"offering_name": "13th Sabbath Offering", "offering_category": "Special Offering", "is_remittable": 1},
		{"offering_name": "Investment Offering", "offering_category": "Special Offering", "is_remittable": 1},
		{"offering_name": "Birthday & Thanksgiving", "offering_category": "Regular Offering", "is_remittable": 0},
		{"offering_name": "Building Fund", "offering_category": "Fund", "is_remittable": 0},
		{"offering_name": "Evangelism Fund", "offering_category": "Fund", "is_remittable": 0},
		{"offering_name": "Camp Meeting Offering", "offering_category": "Special Offering", "is_remittable": 1},
		{"offering_name": "Special Offering", "offering_category": "Special Offering", "is_remittable": 0},
	]
	for ot in offering_types:
		if not frappe.db.exists("Offering Type", {"offering_name": ot["offering_name"]}):
			doc = frappe.get_doc({"doctype": "Offering Type", "enabled": 1, **ot})
			doc.insert(ignore_permissions=True)
