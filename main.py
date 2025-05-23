#!/usr/bin/env python
"""
FabricFriend - Console Application for Microsoft Fabric and Power BI Management

This application uses the Azure Python SDK and Microsoft 365 SDK to gather information 
on Fabric instances and Power BI Premium instances.
"""

import argparse
import logging
import sys
from rich.console import Console
from rich.logging import RichHandler
from typing import Optional, List

# Import modules and utilities
from modules import FabricManager, PowerBIManager
from utils import initialize_credential, console, display_results, check_azure_auth, check_microsoft365_auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("fabric_friend")

def list_fabric_instances(args):
    """
    List all Microsoft Fabric instances in the specified subscription.
    
    Args:
        args: Command line arguments
    """
    credential = initialize_credential()
    console.print("[bold]Fetching Microsoft Fabric instances...[/bold]")
    
    # Create Fabric manager
    fabric_manager = FabricManager(credential, args.subscription_id)
    
    # Get instances
    instances = fabric_manager.list_instances(args.resource_group)
    
    # TODO: Implement display logic when API is implemented
    console.print("[yellow]Feature not yet implemented[/yellow]")

def list_powerbi_premium(args):
    """
    List all Power BI Premium instances in the specified subscription.
    
    Args:
        args: Command line arguments
    """
    credential = initialize_credential()
    console.print("[bold]Fetching Power BI Premium instances...[/bold]")
    
    # Create Power BI manager
    powerbi_manager = PowerBIManager(credential, args.subscription_id)
    
    # Get instances
    instances = powerbi_manager.list_premium_instances(args.resource_group)
    
    # TODO: Implement display logic when API is implemented
    console.print("[yellow]Feature not yet implemented[/yellow]")

def check_auth(args):
    """
    Check authentication status with Azure and Microsoft 365.
    
    Args:
        args: Command line arguments
    """
    console.print("[bold]Checking authentication status...[/bold]")
    
    # Check Azure authentication
    azure_auth_success = check_azure_auth()
    if azure_auth_success:
        console.print("✅ [green]Azure authentication successful[/green]")
    else:
        console.print("❌ [red]Azure authentication failed[/red]")
    
    # Check Microsoft 365 authentication
    m365_auth_success = check_microsoft365_auth()
    if m365_auth_success:
        console.print("✅ [green]Microsoft 365 authentication successful[/green]")
    else:
        console.print("[yellow]Microsoft 365 authentication check not yet implemented[/yellow]")

def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(
        description="FabricFriend - Microsoft Fabric and Power BI Management Tool"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Fabric instances command
    fabric_parser = subparsers.add_parser("fabric", help="List Microsoft Fabric instances")
    fabric_parser.add_argument("-s", "--subscription-id", required=True, help="Azure Subscription ID")
    fabric_parser.add_argument("-g", "--resource-group", help="Resource group name")
    fabric_parser.set_defaults(func=list_fabric_instances)
    
    # Power BI Premium command
    powerbi_parser = subparsers.add_parser("powerbi", help="List Power BI Premium instances")
    powerbi_parser.add_argument("-s", "--subscription-id", required=True, help="Azure Subscription ID")
    powerbi_parser.add_argument("-g", "--resource-group", help="Resource group name")
    powerbi_parser.set_defaults(func=list_powerbi_premium)
    
    # Auth check command
    auth_parser = subparsers.add_parser("auth", help="Check authentication status")
    auth_parser.set_defaults(func=check_auth)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Display header
    console.print("[bold blue]FabricFriend[/bold blue] - Microsoft Fabric and Power BI Management Tool")
    
    # Run the specified command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
