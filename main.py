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
from utils import initialize_credential, console, display_results, check_azure_auth, load_and_run

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("fabric_friend")

def check_auth(args):
    """
    Check authentication status with Azure.
    
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

def run_module(args):
    """
    Run a module using the module loader.
    
    Each module has a standard 'run' function that serves as the entry point.
    If a command is specified, it will be passed to the module's run function
    or directly executed if the module has a specific function for that command.
    
    Args:
        args: Command line arguments
    """
    try:
        # Prepare arguments for the module
        module_args = vars(args).copy()
        # Remove the module_name, command, and func from the arguments
        module_args.pop("module_name", None)
        module_args.pop("command", None)
        module_args.pop("func", None)
          # Map CLI module names to actual module names if needed
        module_name_map = {
            "topology": "azure_topology"
        }
        
        # Use the mapped module name if available, otherwise use the original
        actual_module_name = module_name_map.get(args.module_name, args.module_name)
          # Determine the command to use
        command = None
        if hasattr(args, "command") and args.command:
            # User provided a specific command, use it
            command = args.command
        
        # Load and run the module with the specified command
        # If command is None, module_loader will use the default 'run' function
        # The 'run' function should handle routing to the correct operation based on its command parameter
        result = load_and_run(
            f"modules.{actual_module_name}", 
            module_args, 
            command
        )
        
        # Display the result
        if hasattr(args, "command") and args.command:
            console.print(f"[bold green]Module {args.module_name} executed command '{args.command}' successfully[/bold green]")
        else:
            console.print(f"[bold green]Module {args.module_name} executed successfully[/bold green]")
        
        # TODO: Implement a more sophisticated result display
        console.print(result)
        
    except Exception as e:
        if hasattr(args, "command") and args.command:
            console.print(f"[bold red]Error running module {args.module_name} command '{args.command}': {str(e)}[/bold red]")
            log.exception(f"Error running module {args.module_name} command '{args.command}'")
        else:
            console.print(f"[bold red]Error running module {args.module_name}: {str(e)}[/bold red]")
            log.exception(f"Error running module {args.module_name}")
        sys.exit(1)

# Global parser objects to be accessible across functions
parser = None
module_subparsers = {}

def main():
    """
    Main entry point for the application.
    
    Supports Docker-like CLI structure:
    fabricfriend [module] [command] [arguments]
    """
    global parser, module_subparsers
    
    parser = argparse.ArgumentParser(
        description="FabricFriend - Microsoft Fabric and Power BI Management Tool"
    )
    
    # Create subparsers for modules
    subparsers = parser.add_subparsers(dest="module_name", help="Module to run")
    
    # Fabric module
    fabric_parser = subparsers.add_parser("fabric", help="Microsoft Fabric operations")
    fabric_subparsers = fabric_parser.add_subparsers(dest="command", help="Command to run")
    
    # Fabric list command
    fabric_list_parser = fabric_subparsers.add_parser("list", help="List Microsoft Fabric instances")
    fabric_list_parser.add_argument("-s", "--subscription-id", required=True, help="Azure Subscription ID")
    fabric_list_parser.add_argument("-g", "--resource-group", help="Resource group name")
    
    # Fabric get command
    fabric_get_parser = fabric_subparsers.add_parser("get", help="Get Microsoft Fabric instance details")
    fabric_get_parser.add_argument("-s", "--subscription-id", required=True, help="Azure Subscription ID")
    fabric_get_parser.add_argument("-i", "--instance-id", required=True, help="Instance ID")
    
    # Power BI module
    powerbi_parser = subparsers.add_parser("powerbi", help="Power BI operations")
    powerbi_subparsers = powerbi_parser.add_subparsers(dest="command", help="Command to run")
    
    # Power BI list command
    powerbi_list_parser = powerbi_subparsers.add_parser("list", help="List Power BI Premium instances")
    powerbi_list_parser.add_argument("-s", "--subscription-id", required=True, help="Azure Subscription ID")
    powerbi_list_parser.add_argument("-g", "--resource-group", help="Resource group name")
    
    # Power BI scan-data command
    powerbi_scan_parser = powerbi_subparsers.add_parser("scan-data", help="Scan Power BI data")
    powerbi_scan_parser.add_argument("-s", "--subscription-id", required=True, help="Azure Subscription ID")
    powerbi_scan_parser.add_argument("-i", "--instance-id", help="Instance ID")    # Azure Topology module
    topology_parser = subparsers.add_parser("topology", help="Azure resource topology operations")
    topology_subparsers = topology_parser.add_subparsers(dest="command", help="Command to run")
    module_subparsers["topology"] = topology_subparsers
      # Azure Topology collect command
    topology_collect_parser = topology_subparsers.add_parser("collect", help="Collect Azure topology data (subscriptions, management groups, resource groups, resources)")
    topology_collect_parser.add_argument("-s", "--subscription-id", required=False, help="Azure Subscription ID (optional - will collect data from all accessible subscriptions if not specified)")
    topology_collect_parser.add_argument("-o", "--output-dir", default="./outputs", help="Output directory for CSV files (default: ./outputs)")
    
    # Azure Topology visualize command
    topology_visualize_parser = topology_subparsers.add_parser("visualize", help="Visualize Azure resource topology")
    topology_visualize_parser.add_argument("-s", "--subscription-id", required=False, help="Azure Subscription ID (optional - will visualize all accessible subscriptions if not specified)")
    topology_visualize_parser.add_argument("-o", "--output-dir", default="./outputs", help="Output directory for visualization files (default: ./outputs)")
    topology_visualize_parser.add_argument("-t", "--resource-type", help="Resource type filter")
    
    # Authentication module
    auth_parser = subparsers.add_parser("auth", help="Authentication operations")
    auth_subparsers = auth_parser.add_subparsers(dest="command", help="Command to run")
    
    # Auth check command
    auth_check_parser = auth_subparsers.add_parser("check", help="Check authentication status")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Display header
    console.print("[bold blue]FabricFriend[/bold blue] - Microsoft Fabric and Power BI Management Tool")
    # Handle auth core util commands separately (do not load via module loader)
    if args.module_name == "auth":
        if args.command == "check":
            check_auth(args)
            sys.exit(0)
        auth_parser.print_help()
        sys.exit(1)

    # Run the specified module and command
    if hasattr(args, "module_name") and args.module_name:
        run_module(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
