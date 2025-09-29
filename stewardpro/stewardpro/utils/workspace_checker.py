# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
import os


def check_and_update_workspace():
    """
    Comprehensive workspace checker and updater for StewardPro.
    
    This function:
    1. Checks if StewardPro workspace exists
    2. Verifies workspace visibility and accessibility
    3. Updates workspace configuration if needed
    4. Ensures all reports and doctypes are properly linked
    5. Makes the workspace visible to users
    
    Returns:
        dict: Status report of workspace check and updates
    """
    
    print("🔍 Starting StewardPro Workspace Check...")
    print("=" * 50)
    
    results = {
        "workspace_exists": False,
        "workspace_visible": False,
        "workspace_public": False,
        "links_count": 0,
        "reports_linked": 0,
        "doctypes_linked": 0,
        "updates_made": [],
        "errors": [],
        "status": "unknown"
    }
    
    try:
        # Step 1: Check if workspace exists
        workspace_name = "StewardPro"
        workspace_doc = None
        
        print(f"📋 Step 1: Checking if '{workspace_name}' workspace exists...")
        
        try:
            workspace_doc = frappe.get_doc("Workspace", workspace_name)
            results["workspace_exists"] = True
            print(f"✅ Workspace '{workspace_name}' found!")
            print(f"   - Label: {workspace_doc.label}")
            print(f"   - Title: {workspace_doc.title}")
            print(f"   - Module: {workspace_doc.module}")
            
        except frappe.DoesNotExistError:
            print(f"❌ Workspace '{workspace_name}' not found!")
            results["errors"].append(f"Workspace '{workspace_name}' does not exist")
            return create_workspace_if_missing(results)
        
        # Step 2: Check workspace visibility and accessibility
        print(f"\n📋 Step 2: Checking workspace visibility...")
        
        results["workspace_public"] = workspace_doc.public
        results["workspace_visible"] = not workspace_doc.is_hidden
        
        print(f"   - Public: {workspace_doc.public}")
        print(f"   - Hidden: {workspace_doc.is_hidden}")
        print(f"   - For User: {workspace_doc.for_user or 'All Users'}")
        
        # Step 3: Check workspace links
        print(f"\n📋 Step 3: Analyzing workspace links...")
        
        links = workspace_doc.links or []
        results["links_count"] = len(links)
        
        reports_count = len([link for link in links if link.link_type == "Report"])
        doctypes_count = len([link for link in links if link.link_type == "DocType"])
        
        results["reports_linked"] = reports_count
        results["doctypes_linked"] = doctypes_count
        
        print(f"   - Total Links: {len(links)}")
        print(f"   - Reports: {reports_count}")
        print(f"   - DocTypes: {doctypes_count}")
        
        # Step 4: Verify key reports are linked
        print(f"\n📋 Step 4: Verifying key reports are linked...")
        
        key_reports = [
            "Financial Summary",
            "Tithes and Offerings Report", 
            "Building Fund Report",
            "Annual Report",
            "Departmental Budget Report",
            "Expense Report"
        ]
        
        linked_reports = [link.link_to for link in links if link.link_type == "Report"]
        missing_reports = [report for report in key_reports if report not in linked_reports]
        
        if missing_reports:
            print(f"⚠️  Missing reports in workspace: {', '.join(missing_reports)}")
            results["errors"].append(f"Missing reports: {', '.join(missing_reports)}")
        else:
            print(f"✅ All key reports are linked!")
        
        # Step 5: Update workspace if needed
        print(f"\n📋 Step 5: Updating workspace configuration...")
        
        updates_needed = False
        
        # Make workspace visible if hidden
        if workspace_doc.is_hidden:
            print("🔧 Making workspace visible...")
            workspace_doc.is_hidden = 0
            updates_needed = True
            results["updates_made"].append("Made workspace visible")
        
        # Make workspace public if not already
        if not workspace_doc.public:
            print("🔧 Making workspace public...")
            workspace_doc.public = 1
            updates_needed = True
            results["updates_made"].append("Made workspace public")
        
        # Add missing reports
        if missing_reports:
            print("🔧 Adding missing reports to workspace...")
            add_missing_reports_to_workspace(workspace_doc, missing_reports)
            updates_needed = True
            results["updates_made"].append(f"Added {len(missing_reports)} missing reports")
        
        # Save updates if any were made
        if updates_needed:
            workspace_doc.save(ignore_permissions=True)
            print("💾 Workspace updates saved!")
        else:
            print("✅ No updates needed - workspace is properly configured!")
        
        # Step 6: Final verification
        print(f"\n📋 Step 6: Final verification...")
        
        # Reload workspace to verify changes
        workspace_doc.reload()
        
        results["workspace_visible"] = not workspace_doc.is_hidden
        results["workspace_public"] = workspace_doc.public
        results["links_count"] = len(workspace_doc.links or [])
        
        print(f"   - Workspace visible: {not workspace_doc.is_hidden}")
        print(f"   - Workspace public: {workspace_doc.public}")
        print(f"   - Total links: {len(workspace_doc.links or [])}")
        
        # Determine final status
        if results["workspace_visible"] and results["workspace_public"] and not missing_reports:
            results["status"] = "success"
            print(f"\n🎉 SUCCESS: StewardPro workspace is properly configured and visible!")
        else:
            results["status"] = "partial_success"
            print(f"\n⚠️  PARTIAL SUCCESS: Some issues may remain")
        
    except Exception as e:
        error_msg = f"Error during workspace check: {str(e)}"
        print(f"\n❌ ERROR: {error_msg}")
        results["errors"].append(error_msg)
        results["status"] = "error"
        
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Workspace Check Complete!")
    print(f"📊 Final Status: {results['status'].upper()}")
    
    return results


def create_workspace_if_missing(results):
    """Create StewardPro workspace if it doesn't exist"""
    
    print("\n🔧 Creating missing StewardPro workspace...")
    
    try:
        # Check if workspace JSON file exists
        workspace_json_path = frappe.get_app_path("stewardpro", "stewardpro", "workspace", "stewardpro", "stewardpro.json")
        
        if os.path.exists(workspace_json_path):
            print(f"📁 Found workspace JSON file: {workspace_json_path}")
            
            # Import workspace from JSON
            with open(workspace_json_path, 'r') as f:
                workspace_data = json.load(f)
            
            # Create workspace document
            workspace_doc = frappe.get_doc(workspace_data)
            workspace_doc.insert(ignore_permissions=True)
            
            print(f"✅ Workspace created successfully from JSON file!")
            results["updates_made"].append("Created workspace from JSON file")
            results["workspace_exists"] = True
            results["status"] = "created"
            
        else:
            print(f"❌ Workspace JSON file not found at: {workspace_json_path}")
            results["errors"].append("Workspace JSON file not found")
            results["status"] = "error"
            
    except Exception as e:
        error_msg = f"Error creating workspace: {str(e)}"
        print(f"❌ {error_msg}")
        results["errors"].append(error_msg)
        results["status"] = "error"
    
    return results


def add_missing_reports_to_workspace(workspace_doc, missing_reports):
    """Add missing reports to workspace"""
    
    for report_name in missing_reports:
        try:
            # Check if report exists
            if frappe.db.exists("Report", report_name):
                # Add report link to workspace
                workspace_doc.append("links", {
                    "label": report_name,
                    "link_type": "Report",
                    "link_to": report_name,
                    "is_query_report": 1,
                    "hidden": 0,
                    "onboard": 0,
                    "type": "Link"
                })
                print(f"   ✅ Added report: {report_name}")
            else:
                print(f"   ⚠️  Report not found: {report_name}")
                
        except Exception as e:
            print(f"   ❌ Error adding report {report_name}: {str(e)}")


@frappe.whitelist()
def run_workspace_check():
    """API endpoint to run workspace check"""
    return check_and_update_workspace()


def test_workspace_access():
    """Test if current user can access StewardPro workspace"""
    
    print("🧪 Testing workspace access...")
    
    try:
        # Get workspace sidebar items
        sidebar_items = frappe.call("frappe.desk.desktop.get_workspace_sidebar_items")
        
        # Check if StewardPro is in the list
        stewardpro_found = False
        for page in sidebar_items.get("pages", []):
            if page.get("name") == "StewardPro" or page.get("title") == "StewardPro":
                stewardpro_found = True
                print(f"✅ StewardPro workspace found in sidebar!")
                print(f"   - Title: {page.get('title')}")
                print(f"   - Public: {page.get('public')}")
                print(f"   - Hidden: {page.get('is_hidden')}")
                break
        
        if not stewardpro_found:
            print(f"❌ StewardPro workspace not found in sidebar!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing workspace access: {str(e)}")
        return False


if __name__ == "__main__":
    # Run the workspace check
    results = check_and_update_workspace()
    
    # Test workspace access
    test_workspace_access()
    
    # Print summary
    print(f"\n📋 SUMMARY:")
    print(f"   - Workspace exists: {results['workspace_exists']}")
    print(f"   - Workspace visible: {results['workspace_visible']}")
    print(f"   - Workspace public: {results['workspace_public']}")
    print(f"   - Total links: {results['links_count']}")
    print(f"   - Updates made: {len(results['updates_made'])}")
    print(f"   - Errors: {len(results['errors'])}")
    print(f"   - Final status: {results['status']}")
