"""
Azure Topology Visualization Utilities

This module contains visualization functions for Azure topology data.
These functions create various network graphs and charts to visualize the 
hierarchical relationships between Azure resources.
"""

import os
import logging
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Dict, Optional

log = logging.getLogger("fabric_friend")

def create_azure_topology_visualizations(output_dir: str, csv_schemas: Optional[Dict[str, List[str]]] = None) -> bool:
    """
    Create all Azure topology visualizations from collected data.
    
    Args:
        output_dir: Directory where the CSV files are located and where visualizations will be saved
        csv_schemas: Optional dictionary containing CSV schemas for creating empty DataFrames when files are missing
        
    Returns:
        bool: True if all visualizations were created successfully, False otherwise
    """
    from utils import console
    
    console.print("[blue]Creating visualizations from topology data...[/blue]")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Load data from CSV files
        subscriptions_file = os.path.join(output_dir, "subscriptions.csv")
        mgmt_groups_file = os.path.join(output_dir, "management_groups.csv")
        resource_groups_file = os.path.join(output_dir, "resource_groups.csv")
        resources_file = os.path.join(output_dir, "resources.csv")
        
        # Check if files exist
        if not os.path.exists(subscriptions_file):
            console.print("[red]Error: Subscriptions data file not found. Run 'collect' command first.[/red]")
            return False
        
        # Load data using pandas
        console.print("[yellow]Loading data from CSV files...[/yellow]")
        subscriptions_df = pd.read_csv(subscriptions_file)
          # Management groups might be empty if user doesn't have permissions
        try:
            if os.path.exists(mgmt_groups_file) and os.path.getsize(mgmt_groups_file) > 0:
                mgmt_groups_df = pd.read_csv(mgmt_groups_file)
            else:
                # Use provided schema or fallback to basic columns
                if csv_schemas and 'management_groups' in csv_schemas:
                    mgmt_groups_df = pd.DataFrame(columns=csv_schemas['management_groups'])
                else:
                    mgmt_groups_df = pd.DataFrame(columns=['id', 'name', 'display_name', 'tenant_id', 'type'])
                console.print("[yellow]Warning: No management groups data available.[/yellow]")
        except Exception as e:
            # Use provided schema or fallback to basic columns
            if csv_schemas and 'management_groups' in csv_schemas:
                mgmt_groups_df = pd.DataFrame(columns=csv_schemas['management_groups'])
            else:
                mgmt_groups_df = pd.DataFrame(columns=['id', 'name', 'display_name', 'tenant_id', 'type'])
            console.print(f"[yellow]Warning: Failed to load management groups data: {e}[/yellow]")
        
        resource_groups_df = pd.read_csv(resource_groups_file)
        resources_df = pd.read_csv(resources_file)
        
        # Create the visualizations
        console.print("[yellow]Creating visualizations...[/yellow]")
        
        # 1. Management Groups and Subscriptions
        create_mgmt_group_subscription_viz(mgmt_groups_df, subscriptions_df, output_dir)
        
        # 2. Subscriptions and Resource Groups
        create_subscription_resource_group_viz(subscriptions_df, resource_groups_df, output_dir)
        
        # 3. Resource Groups and Resources
        create_resource_group_resources_viz(resource_groups_df, resources_df, output_dir)
        
        # 4. Complete hierarchy visualization
        create_complete_hierarchy_viz(mgmt_groups_df, subscriptions_df, resource_groups_df, resources_df, output_dir)
        
        console.print("[green]Visualization creation completed successfully![/green]")
        return True
        
    except Exception as e:
        log.error(f"Error creating visualizations: {e}")
        console.print(f"[red]Error creating visualizations: {str(e)}[/red]")
        return False

def create_mgmt_group_subscription_viz(mgmt_groups_df: pd.DataFrame, subscriptions_df: pd.DataFrame, output_dir: str):
    """Create a visualization of management groups and their subscriptions."""
    from utils import console
    
    try:
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add management groups to the graph
        mgmt_group_nodes = []
        if not mgmt_groups_df.empty:
            for _, row in mgmt_groups_df.iterrows():
                node_id = row['name']
                G.add_node(node_id, label=row['display_name'] or row['name'], type='management_group')
                mgmt_group_nodes.append(node_id)
        
        # Add subscriptions to the graph
        sub_nodes = []
        for _, row in subscriptions_df.iterrows():
            node_id = row['subscription_id']
            G.add_node(node_id, label=row['display_name'], type='subscription')
            sub_nodes.append(node_id)
            
            # Connect to management groups if available
            # Note: This is a simplification - in a real implementation, you'd query the 
            # management group structure to know exactly which subscription belongs to which group
            if mgmt_group_nodes:
                # For demo purposes, connect to the first management group
                # In a real scenario, you'd determine the actual parent-child relationship
                G.add_edge(mgmt_group_nodes[0], node_id)
        
        # Create visualization
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes - group by type for consistent coloring
        mgmt_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'management_group']
        sub_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'subscription']
        
        # Draw management group nodes
        if mgmt_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=mgmt_nodes, node_color='#4287f5', node_size=500, alpha=0.8)
        
        # Draw subscription nodes
        if sub_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=sub_nodes, node_color='#42c5f5', node_size=500, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, width=1.0)
        
        # Draw labels
        labels = {n: G.nodes[n]['label'] for n in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color='black')
        
        plt.title("Azure Management Groups and Subscriptions")
        plt.axis('off')
        
        # Save the visualization
        file_path = os.path.join(output_dir, "mgmt_groups_subscriptions.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]Created management groups and subscriptions visualization: {file_path}[/green]")
        
    except Exception as e:
        log.error(f"Error creating management groups and subscriptions visualization: {e}")
        console.print(f"[red]Failed to create management groups and subscriptions visualization: {str(e)}[/red]")

def create_subscription_resource_group_viz(subscriptions_df: pd.DataFrame, resource_groups_df: pd.DataFrame, output_dir: str):
    """Create a visualization of subscriptions and their resource groups."""
    from utils import console
    
    try:
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add subscriptions to the graph
        for _, row in subscriptions_df.iterrows():
            sub_id = row['subscription_id']
            G.add_node(sub_id, label=row['display_name'], type='subscription')
        
        # Add resource groups to the graph and connect to their subscription
        for _, row in resource_groups_df.iterrows():
            rg_id = row['id']
            sub_id = row['subscription_id']
            
            G.add_node(rg_id, label=row['name'], type='resource_group')
            if sub_id in G:
                G.add_edge(sub_id, rg_id)
        
        # Create visualization
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes by type for consistent coloring
        sub_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'subscription']
        rg_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'resource_group']
        
        # Draw subscription nodes
        if sub_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=sub_nodes, node_color='#4287f5', node_size=500, alpha=0.8)
        
        # Draw resource group nodes
        if rg_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=rg_nodes, node_color='#42f59e', node_size=500, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, width=1.0)
        
        # Draw labels
        labels = {n: G.nodes[n]['label'] for n in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color='black')
        
        plt.title("Azure Subscriptions and Resource Groups")
        plt.axis('off')
        
        # Save the visualization
        file_path = os.path.join(output_dir, "subscriptions_resource_groups.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]Created subscriptions and resource groups visualization: {file_path}[/green]")
        
    except Exception as e:
        log.error(f"Error creating subscriptions and resource groups visualization: {e}")
        console.print(f"[red]Failed to create subscriptions and resource groups visualization: {str(e)}[/red]")

def create_resource_group_resources_viz(resource_groups_df: pd.DataFrame, resources_df: pd.DataFrame, output_dir: str):
    """Create a visualization of resource groups and their resources."""
    from utils import console
    
    try:
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add resource groups to the graph
        for _, row in resource_groups_df.iterrows():
            rg_id = row['id']
            G.add_node(rg_id, label=row['name'], type='resource_group')
        
        # Add resources to the graph (limiting to a manageable number for visualization)
        # Group resources by type to reduce graph complexity
        resources_by_type = {}
        for _, row in resources_df.iterrows():
            rg_name = row['resource_group']
            resource_type = row['type']
            
            # Find the resource group node
            rg_node = None
            for rg_id in G.nodes():
                if G.nodes[rg_id]['type'] == 'resource_group' and G.nodes[rg_id]['label'] == rg_name:
                    rg_node = rg_id
                    break
            
            if rg_node:
                # Create a composite key for resource types in this resource group
                key = f"{rg_node}_{resource_type}"
                
                if key not in resources_by_type:
                    # Create a resource type node
                    resource_type_node = f"{resource_type}_{rg_name}"
                    G.add_node(resource_type_node, label=resource_type.split('/')[-1], type='resource_type')
                    G.add_edge(rg_node, resource_type_node)
                    
                    resources_by_type[key] = {
                        'node': resource_type_node,
                        'count': 1
                    }
                else:
                    resources_by_type[key]['count'] += 1
        
        # Update labels for resource type nodes to include counts
        for key, info in resources_by_type.items():
            node = info['node']
            current_label = G.nodes[node]['label']
            G.nodes[node]['label'] = f"{current_label} ({info['count']})"
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes by type for consistent coloring
        rg_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'resource_group']
        resource_type_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'resource_type']
        
        # Draw resource group nodes
        if rg_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=rg_nodes, node_color='#42f59e', node_size=500, alpha=0.8)
        
        # Draw resource type nodes
        if resource_type_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=resource_type_nodes, node_color='#f5d442', node_size=500, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, width=1.0)
        
        # Draw labels
        labels = {n: G.nodes[n]['label'] for n in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_color='black')
        
        plt.title("Azure Resource Groups and Resource Types")
        plt.axis('off')
        
        # Save the visualization
        file_path = os.path.join(output_dir, "resource_groups_resources.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]Created resource groups and resources visualization: {file_path}[/green]")
        
    except Exception as e:
        log.error(f"Error creating resource groups and resources visualization: {e}")
        console.print(f"[red]Failed to create resource groups and resources visualization: {str(e)}[/red]")

def create_complete_hierarchy_viz(mgmt_groups_df: pd.DataFrame, subscriptions_df: pd.DataFrame, 
                                 resource_groups_df: pd.DataFrame, resources_df: pd.DataFrame, output_dir: str):
    """Create a visualization of the complete Azure hierarchy."""
    from utils import console
    
    try:
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add management groups to the graph
        mgmt_group_nodes = []
        if not mgmt_groups_df.empty:
            for _, row in mgmt_groups_df.iterrows():
                node_id = row['name']
                G.add_node(node_id, label=row['display_name'] or row['name'], type='management_group')
                mgmt_group_nodes.append(node_id)
        
        # Add subscriptions to the graph
        for _, row in subscriptions_df.iterrows():
            sub_id = row['subscription_id']
            G.add_node(sub_id, label=row['display_name'], type='subscription')
            
            # Connect to management groups if available
            if mgmt_group_nodes:
                # Simplified connection - in a real implementation, you'd determine the actual parent
                G.add_edge(mgmt_group_nodes[0], sub_id)
        
        # Add resource groups to the graph
        for _, row in resource_groups_df.iterrows():
            rg_id = row['id']
            sub_id = row['subscription_id']
            
            G.add_node(rg_id, label=row['name'], type='resource_group')
            if sub_id in G:
                G.add_edge(sub_id, rg_id)
        
        # Add aggregated resources by type to keep the graph manageable
        resource_types = {}
        for _, row in resources_df.iterrows():
            rg_name = row['resource_group']
            resource_type = row['type']
            
            # Find the resource group node
            rg_node = None
            for rg_id in G.nodes():
                if G.nodes[rg_id]['type'] == 'resource_group' and G.nodes[rg_id]['label'] == rg_name:
                    rg_node = rg_id
                    break
            
            if rg_node:
                # Create a composite key for resource types in this resource group
                key = f"{rg_node}_{resource_type}"
                
                if key not in resource_types:
                    # Create a resource type node
                    resource_type_node = f"{resource_type}_{rg_name}"
                    G.add_node(resource_type_node, label=resource_type.split('/')[-1], type='resource_type')
                    G.add_edge(rg_node, resource_type_node)
                    
                    resource_types[key] = {
                        'node': resource_type_node,
                        'count': 1
                    }
                else:
                    resource_types[key]['count'] += 1
        
        # Update labels for resource type nodes to include counts
        for key, info in resource_types.items():
            node = info['node']
            current_label = G.nodes[node]['label']
            G.nodes[node]['label'] = f"{current_label} ({info['count']})"
        
        # Create visualization
        plt.figure(figsize=(20, 16))
        
        # Use hierarchical layout if graphviz is available, otherwise use spring layout
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=TB')
        except:
            # Fallback to spring layout if graphviz is not available
            pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes by type for consistent coloring
        mgmt_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'management_group']
        sub_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'subscription']
        rg_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'resource_group']
        resource_type_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'resource_type']
        
        # Draw management group nodes
        if mgmt_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=mgmt_nodes, node_color='#4287f5', node_size=400, alpha=0.8)  # Blue
        
        # Draw subscription nodes
        if sub_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=sub_nodes, node_color='#42c5f5', node_size=400, alpha=0.8)  # Light blue
        
        # Draw resource group nodes
        if rg_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=rg_nodes, node_color='#42f59e', node_size=400, alpha=0.8)  # Green
        
        # Draw resource type nodes
        if resource_type_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=resource_type_nodes, node_color='#f5d442', node_size=400, alpha=0.8)  # Yellow
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=10, width=0.8)
        
        # Draw labels
        labels = {n: G.nodes[n]['label'] for n in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color='black')
        
        plt.title("Complete Azure Resource Hierarchy")
        plt.axis('off')
        
        # Save the visualization
        file_path = os.path.join(output_dir, "complete_azure_hierarchy.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]Created complete Azure hierarchy visualization: {file_path}[/green]")
        
    except Exception as e:
        log.error(f"Error creating complete hierarchy visualization: {e}")
        console.print(f"[red]Failed to create complete hierarchy visualization: {str(e)}[/red]")
