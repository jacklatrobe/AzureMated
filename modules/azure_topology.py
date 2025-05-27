"""
Azure Topology Module

This module implements functionality for collecting Azure topology data including subscriptions,
management groups, resource groups, and resources. It collects organization-wide metadata and
writes the results to CSV files for analysis.

Module Structure for Module Loader Compatibility:
-------------------------------------------------
1. Each module must define a 'run' function at the module level that serves as the entry point
2. The 'run' function must accept these standard parameters:
   - subscription_id: The Azure subscription ID (required)
   - Any additional parameters needed for the specific module
   - **kwargs: To capture any extra parameters passed by the module_loader
3. The 'run' function should return a dictionary with results
4. The module typically defines a manager class to encapsulate module-specific functionality
5. The module should maintain a singleton instance of the manager for efficiency

When creating new modules, follow this pattern to ensure compatibility with the module_loader.
"""

from azure.identity import ChainedTokenCredential
from azure.core.exceptions import AzureError
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.managementgroups import ManagementGroupsAPI
import csv
import logging
import os
from typing import List, Dict, Optional, Mapping
import time

log = logging.getLogger("fabric_friend")

# Define schemas for different CSV file types
CSV_SCHEMAS = {
    'subscriptions': ['subscription_id', 'display_name', 'state', 'tenant_id', 'authorization_source'],
    'management_groups': ['id', 'name', 'display_name', 'tenant_id', 'type'],
    'resource_groups': ['subscription_id', 'name', 'location', 'id', 'type', 'provisioning_state', 'tags'],
    'resources': ['subscription_id', 'resource_group', 'name', 'type', 'location', 'id', 'kind', 'sku', 'tags'],
    # Generic fallback for unknown file types
    'default': ['id', 'name', 'type']
}

class AzureTopologyManager:
    """Manager for collecting Azure topology data including subscriptions, management groups, and resources."""
    
    def __init__(self, credential: ChainedTokenCredential, subscription_id: Optional[str] = None):
        """
        Initialize the AzureTopologyManager.
        
        Args:
            credential: The Azure credential using chained authentication
            subscription_id: Optional Azure subscription ID for specific operations
        """
        self.credential = credential
        self.subscription_id = subscription_id
        self._subscription_client: Optional[SubscriptionClient] = None
        self._resource_client: Optional[ResourceManagementClient] = None
        self._management_groups_client: Optional[ManagementGroupsAPI] = None

    def _get_subscription_client(self) -> SubscriptionClient:
        """Get or create the subscription client with retry logic."""
        if self._subscription_client is None:
            try:
                self._subscription_client = SubscriptionClient(self.credential)
            except Exception as e:
                log.error(f"Failed to create subscription client: {e}")
                raise AzureError(f"Failed to initialize subscription client: {e}")
        return self._subscription_client

    def _get_resource_client(self, subscription_id: str) -> ResourceManagementClient:
        """Get or create the resource management client for a specific subscription."""
        try:
            return ResourceManagementClient(self.credential, subscription_id)
        except Exception as e:
            log.error(f"Failed to create resource client for subscription {subscription_id}: {e}")
            raise AzureError(f"Failed to initialize resource client: {e}")

    def _get_management_groups_client(self) -> ManagementGroupsAPI:
        """Get or create the management groups client."""
        if self._management_groups_client is None:
            try:
                self._management_groups_client = ManagementGroupsAPI(self.credential)
            except Exception as e:
                log.error(f"Failed to create management groups client: {e}")
                raise AzureError(f"Failed to initialize management groups client: {e}")
        return self._management_groups_client

    def get_subscriptions(self) -> List[Dict]:
        """
        Get all Azure subscriptions accessible to the authenticated user.
        
        Returns:
            List of dictionaries containing subscription information
        """
        log.info("Fetching all accessible subscriptions")
        subscriptions = []
        
        try:
            client = self._get_subscription_client()
            
            # Get all subscriptions with retry logic
            for attempt in range(3):
                try:
                    for subscription in client.subscriptions.list():
                        sub_dict = {
                            'subscription_id': subscription.subscription_id,
                            'display_name': subscription.display_name,
                            'state': subscription.state,
                            'tenant_id': getattr(subscription, 'tenant_id', ''),
                            'authorization_source': getattr(subscription, 'authorization_source', ''),
                            'managed_by_tenants': str(getattr(subscription, 'managed_by_tenants', [])),
                        }
                        subscriptions.append(sub_dict)
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        log.error(f"Failed to fetch subscriptions after 3 attempts: {e}")
                        raise AzureError(f"Failed to fetch subscriptions: {e}")
                    log.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        except Exception as e:
            log.error(f"Error fetching subscriptions: {e}")
            raise
            
        log.info(f"Found {len(subscriptions)} subscriptions")
        return subscriptions

    def get_management_groups(self) -> List[Dict]:
        """
        Get all Azure management groups accessible to the authenticated user.
        
        Returns:
            List of dictionaries containing management group information
            Empty list if unauthorized or error occurs
        """
        log.info("Fetching management groups")
        management_groups = []
        
        try:
            client = self._get_management_groups_client()
            
            # Get all management groups with retry logic
            for attempt in range(3):
                try:
                    for mg in client.management_groups.list():
                        # Handle potential attribute errors by using getattr with defaults
                        mg_dict = {
                            'id': getattr(mg, 'id', ''),
                            'name': getattr(mg, 'name', ''),
                            'display_name': getattr(mg, 'display_name', ''),
                            'tenant_id': getattr(mg, 'tenant_id', ''),
                            'type': getattr(mg, 'type', ''),
                        }
                        management_groups.append(mg_dict)
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        # Log error but don't raise
                        log.error(f"Failed to fetch management groups after 3 attempts: {e}")
                        log.warning("Continuing without management groups data")
                        return []
                    log.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        except Exception as e:
            # Log error but don't raise
            log.error(f"Error fetching management groups: {e}")
            log.warning("Continuing without management groups data")
            return []
            
        log.info(f"Found {len(management_groups)} management groups")
        return management_groups

    def get_resource_groups_and_resources(self, subscription_id: str) -> tuple[List[Dict], List[Dict]]:
        """
        Get all resource groups and resources for a specific subscription.
        
        Args:
            subscription_id: The subscription ID to query
            
        Returns:
            Tuple of (resource_groups, resources) as lists of dictionaries
        """
        log.info(f"Fetching resource groups and resources for subscription {subscription_id}")
        resource_groups = []
        resources = []
        
        try:
            client = self._get_resource_client(subscription_id)
            
            # Get resource groups with retry logic
            for attempt in range(3):
                try:
                    for rg in client.resource_groups.list():
                        rg_dict = {
                            'subscription_id': subscription_id,
                            'name': rg.name,
                            'location': rg.location,
                            'id': rg.id,
                            'type': rg.type,
                            'provisioning_state': getattr(rg.properties, 'provisioning_state', ''),
                            'tags': str(rg.tags) if rg.tags else '',
                        }
                        resource_groups.append(rg_dict)
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        log.error(f"Failed to fetch resource groups after 3 attempts: {e}")
                        raise AzureError(f"Failed to fetch resource groups: {e}")
                    log.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2 ** attempt)
            
            # Get all resources with retry logic
            for attempt in range(3):
                try:
                    for resource in client.resources.list():
                        resource_dict = {
                            'subscription_id': subscription_id,
                            'resource_group': resource.id.split('/')[4] if len(resource.id.split('/')) > 4 else '',
                            'name': resource.name,
                            'type': resource.type,
                            'location': resource.location,
                            'id': resource.id,
                            'kind': getattr(resource, 'kind', ''),
                            'sku': str(getattr(resource, 'sku', '')) if hasattr(resource, 'sku') else '',
                            'tags': str(resource.tags) if resource.tags else '',
                        }
                        resources.append(resource_dict)
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        log.error(f"Failed to fetch resources after 3 attempts: {e}")
                        raise AzureError(f"Failed to fetch resources: {e}")
                    log.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2 ** attempt)
                    
        except Exception as e:
            log.error(f"Error fetching resources for subscription {subscription_id}: {e}")
            raise
            
        log.info(f"Found {len(resource_groups)} resource groups and {len(resources)} resources for subscription {subscription_id}")
        return resource_groups, resources

# Create a topology manager instance
_topology_manager = None

def _write_csv(file_path: str, data: List[Dict]) -> None:
    """Write a list of dictionaries to a CSV file. Always creates the file with headers even if there's no data."""
    try:
        if not data:
            log.warning(f"No data to write to {file_path}, creating file with headers only")
            # For empty datasets, use predefined headers from CSV_SCHEMAS
            file_name = os.path.basename(file_path)
            
            # Find the matching schema based on filename
            schema_key = 'default'
            for key in CSV_SCHEMAS:
                if key in file_name:
                    schema_key = key
                    break
            
            fieldnames = CSV_SCHEMAS[schema_key]
        else:
            # Extract field names from the data if we have it
            fieldnames = sorted({key for item in data for key in item.keys()})
        
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            if data:
                writer.writerows(data)
        
        record_count = len(data) if data else 0
        log.info(f"Successfully wrote {record_count} records to {file_path}")
    except Exception as e:
        log.error(f"Failed to write CSV file {file_path}: {e}")
        raise

def run(subscription_id=None, output_dir: str = ".", command=None, **kwargs):
    """
    Run the Azure Topology module functionality.
    
    This function is called by the module_loader and serves as the entry point
    for this module. It collects Azure topology data including subscriptions,
    management groups, resource groups, and resources, then writes them to CSV files.
    
    Module Loader Integration:
    - This function must be defined at the module level (not inside a class)
    - It must accept subscription_id as a parameter
    - It should accept **kwargs to handle any additional parameters
    - It must return a dictionary with the results
    
    Args:
        subscription_id: Optional Azure subscription ID to filter results. If None, collects data from all accessible subscriptions.
        output_dir: Directory where CSV files will be written
        command: The command being executed, used when a specific command function doesn't exist
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with the results of the operation including counts of collected items
    """
    from utils import initialize_credential, console
    
    global _topology_manager
    
    log.info("Running Azure Topology data collection")
    
    # Initialize the credential
    credential = initialize_credential()
    
    # Create or reuse the topology manager
    if _topology_manager is None or (subscription_id and _topology_manager.subscription_id != subscription_id):
        _topology_manager = AzureTopologyManager(credential, subscription_id)

    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Collect subscriptions data
        console.print("[blue]Collecting subscription information...[/blue]")
        subscriptions = _topology_manager.get_subscriptions()
        
        # Collect management groups data
        console.print("[blue]Collecting management groups...[/blue]")
        management_groups = _topology_manager.get_management_groups()
        
        # Collect resource groups and resources for all accessible subscriptions
        console.print("[blue]Collecting resource groups and resources...[/blue]")
        all_resource_groups = []
        all_resources = []
        
        # Filter subscriptions if a specific subscription_id is provided
        target_subscriptions = subscriptions
        if subscription_id:
            target_subscriptions = [sub for sub in subscriptions if sub['subscription_id'] == subscription_id]
            if not target_subscriptions:
                log.warning(f"Specified subscription {subscription_id} not found or not accessible")
                console.print(f"[yellow]Warning: Subscription {subscription_id} not found or not accessible[/yellow]")
        
        for subscription in target_subscriptions:
            sub_id = subscription['subscription_id']
            console.print(f"[yellow]Processing subscription: {subscription['display_name']} ({sub_id})[/yellow]")
            
            try:
                resource_groups, resources = _topology_manager.get_resource_groups_and_resources(sub_id)
                all_resource_groups.extend(resource_groups)
                all_resources.extend(resources)
            except Exception as e:
                log.warning(f"Failed to process subscription {sub_id}: {e}")
                console.print(f"[red]Warning: Could not access subscription {sub_id}: {e}[/red]")
                continue
        
        # Write CSV files
        console.print("[blue]Writing CSV files...[/blue]")
        _write_csv(os.path.join(output_dir, "subscriptions.csv"), subscriptions)
        _write_csv(os.path.join(output_dir, "management_groups.csv"), management_groups)
        _write_csv(os.path.join(output_dir, "resource_groups.csv"), all_resource_groups)
        _write_csv(os.path.join(output_dir, "resources.csv"), all_resources)

        # Create summary
        summary = {
            "subscriptions": len(subscriptions),
            "management_groups": len(management_groups),
            "resource_groups": len(all_resource_groups),
            "resources": len(all_resources),
        }

        console.print(
            f"[green]Azure Topology Collection Complete![/green]\n"
            f"[green]• Subscriptions: {summary['subscriptions']}[/green]\n"
            f"[green]• Management Groups: {summary['management_groups']}[/green]\n"
            f"[green]• Resource Groups: {summary['resource_groups']}[/green]\n"
            f"[green]• Resources: {summary['resources']}[/green]"
        )

        return {"summary": summary}
        
    except Exception as e:
        log.error(f"Failed to collect Azure topology data: {e}")
        console.print(f"[red]Error: {e}[/red]")
        raise
