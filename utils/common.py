"""
Common utilities for FabricFriend.
"""

import logging
from rich.console import Console
from rich.table import Table

console = Console()
log = logging.getLogger("fabric_friend")

def format_table(data, title, columns):
    """
    Format data as a rich table.
    
    Args:
        data: List of dictionaries containing the data
        title: The title of the table
        columns: Dictionary mapping column keys to display names
        
    Returns:
        Rich Table object
    """
    table = Table(title=title)
    
    # Add columns
    for col_key, col_name in columns.items():
        table.add_column(col_name)
        
    # Add rows
    for item in data:
        row = [str(item.get(col_key, "")) for col_key in columns.keys()]
        table.add_row(*row)
        
    return table

def display_results(data, title, columns):
    """
    Display data as a rich table.
    
    Args:
        data: List of dictionaries containing the data
        title: The title of the table
        columns: Dictionary mapping column keys to display names
    """
    if not data:
        console.print(f"[yellow]No {title.lower()} found[/yellow]")
        return
        
    table = format_table(data, title, columns)
    console.print(table)
