# Copyright (c) 2024, StewardPro Team and contributors
# For license information, please see license.txt

import click
import frappe
from frappe.commands import pass_context, get_site


@click.command('check-workspace')
@click.option('--fix', is_flag=True, default=False, help='Automatically fix workspace issues')
@pass_context
def check_workspace(context, fix=False):
    """Check and optionally fix StewardPro workspace configuration"""
    
    site = get_site(context)
    
    with frappe.init_site(site):
        frappe.connect()
        
        from stewardpro.stewardpro.utils.workspace_checker import check_and_update_workspace, test_workspace_access
        
        click.echo("🚀 StewardPro Workspace Checker")
        click.echo("=" * 40)
        
        # Run the workspace check
        results = check_and_update_workspace()
        
        # Test workspace access
        click.echo("\n🧪 Testing workspace access...")
        access_ok = test_workspace_access()
        
        # Display results
        click.echo("\n📊 RESULTS:")
        click.echo("-" * 20)
        
        status_color = "green" if results['status'] == 'success' else "yellow" if results['status'] == 'partial_success' else "red"
        click.echo(f"Status: ", nl=False)
        click.secho(results['status'].upper(), fg=status_color)
        
        click.echo(f"Workspace exists: {'✅' if results['workspace_exists'] else '❌'}")
        click.echo(f"Workspace visible: {'✅' if results['workspace_visible'] else '❌'}")
        click.echo(f"Workspace public: {'✅' if results['workspace_public'] else '❌'}")
        click.echo(f"Access test: {'✅ PASSED' if access_ok else '❌ FAILED'}")
        click.echo(f"Total links: {results['links_count']}")
        click.echo(f"Reports linked: {results['reports_linked']}")
        click.echo(f"DocTypes linked: {results['doctypes_linked']}")
        
        if results['updates_made']:
            click.echo(f"\n🔧 Updates made: {len(results['updates_made'])}")
            for update in results['updates_made']:
                click.echo(f"   - {update}")
        
        if results['errors']:
            click.echo(f"\n❌ Errors: {len(results['errors'])}")
            for error in results['errors']:
                click.secho(f"   - {error}", fg="red")
        
        # Final message
        if results['status'] == 'success':
            click.secho("\n🎉 SUCCESS: StewardPro workspace is properly configured!", fg="green")
        elif results['status'] == 'partial_success':
            click.secho("\n⚠️  PARTIAL SUCCESS: Some issues may remain", fg="yellow")
        else:
            click.secho("\n❌ FAILED: There were errors configuring the workspace", fg="red")


commands = [
    check_workspace
]
