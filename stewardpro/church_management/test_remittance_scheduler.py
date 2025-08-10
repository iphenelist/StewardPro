# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_months, get_first_day, get_last_day, getdate
from stewardpro.church_management.tasks import (
    create_remittance_for_period,
    get_contributions_for_period,
    create_manual_remittance,
    get_remittance_preview
)


def test_remittance_creation():
    """Test function to verify remittance creation functionality"""
    
    print("Testing Remittance Creation Functionality...")
    
    # Test 1: Get contributions for a period
    today = getdate()
    period_start = get_first_day(add_months(today, -1))
    period_end = get_last_day(add_months(today, -1))
    
    print(f"\n1. Testing contributions retrieval for period {period_start} to {period_end}")
    contributions = get_contributions_for_period(period_start, period_end)
    print(f"   Contributions found: {contributions}")
    
    # Test 2: Preview remittance
    print(f"\n2. Testing remittance preview")
    try:
        preview = get_remittance_preview(str(period_start), str(period_end))
        print(f"   Preview data: {preview}")
    except Exception as e:
        print(f"   Preview error: {str(e)}")
    
    # Test 3: Create manual remittance (only if contributions exist)
    if contributions and contributions.get("total_records", 0) > 0:
        print(f"\n3. Testing manual remittance creation")
        try:
            remittance_name = create_manual_remittance(str(period_start), str(period_end), "Monthly")
            print(f"   Created remittance: {remittance_name}")
        except Exception as e:
            print(f"   Creation error: {str(e)}")
    else:
        print(f"\n3. Skipping remittance creation - no contributions found")
    
    print("\nTest completed!")


def create_sample_data():
    """Create sample data for testing"""
    
    print("Creating sample data for testing...")
    
    # Create a sample church member
    if not frappe.db.exists("Church Member", "TEST001"):
        member = frappe.get_doc({
            "doctype": "Church Member",
            "member_id": "TEST001",
            "full_name": "Test Member",
            "status": "Active",
            "role": "Member"
        })
        member.insert(ignore_permissions=True)
        print("   Created test member: TEST001")
    
    # Create sample tithes and offerings
    from frappe.utils import add_days
    
    for i in range(5):
        date = add_days(getdate(), -30 + (i * 5))  # Spread over last month
        
        if not frappe.db.exists("Tithes and Offerings", {"date": date, "member": "TEST001"}):
            tithe_offering = frappe.get_doc({
                "doctype": "Tithes and Offerings",
                "member": "TEST001",
                "date": date,
                "payment_mode": "Cash",
                "tithe_amount": 100 + (i * 10),
                "offering_amount": 50 + (i * 5),
                "campmeeting_offering": 20,
                "church_building_offering": 15
            })
            tithe_offering.insert(ignore_permissions=True)
            tithe_offering.submit()
            print(f"   Created tithes and offerings for {date}")
    
    frappe.db.commit()
    print("Sample data creation completed!")


if __name__ == "__main__":
    # Run this in Frappe console or as a script
    create_sample_data()
    test_remittance_creation()
