"""
CSV Writer Utility

This module provides a centralized CSV writing functionality that accepts schema definitions
from modules. This allows each module to define its own CSV schema and pass it to the
writer, enabling reusability across all modules without circular dependencies.
"""

import csv
import logging
import os
from typing import List, Dict, Optional
from rich.console import Console

log = logging.getLogger("fabric_friend")
console = Console()


def write_csv_with_schema(file_path: str, data: List[Dict], schema: Optional[List[str]] = None) -> None:
    """
    Write a list of dictionaries to a CSV file with an optional schema definition.
    Always creates the file with headers even if there's no data.
    
    Args:
        file_path: Path where the CSV file should be written
        data: List of dictionaries containing the data to write
        schema: Optional list of column names to use as the schema. If provided, 
                this will be used for headers when data is empty. If not provided,
                headers will be derived from the data keys.
                
    Raises:
        Exception: If the file cannot be written
    """
    try:
        if not data:
            log.warning(f"No data to write to {file_path}, creating file with headers only")
            if schema:
                fieldnames = schema
            else:                # Fallback to basic headers if no schema is provided and no data
                fieldnames = ['id', 'name', 'type']
                log.warning(f"No schema provided and no data available. Using default headers: {fieldnames}")
        else:
            if schema:
                # Use only the provided schema fields, ignore extra fields in data
                data_keys = {key for item in data for key in item.keys()}
                extra_keys = data_keys - set(schema)
                if extra_keys:
                    log.warning(f"Data contains keys not in schema: {extra_keys}. These will be ignored.")
                fieldnames = schema
            else:
                # Extract field names from the data if no schema is provided
                fieldnames = sorted({key for item in data for key in item.keys()})
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            if data:
                # If using a schema, ensure all rows have all schema fields (fill missing with empty string)
                if schema:
                    # Filter data to only include schema fields and fill missing fields
                    filtered_data = []
                    for row in data:
                        filtered_row = {field: row.get(field, '') for field in fieldnames}
                        filtered_data.append(filtered_row)
                    writer.writerows(filtered_data)
                else:
                    # No schema, write data as-is
                    writer.writerows(data)
        
        record_count = len(data) if data else 0
        log.info(f"Successfully wrote {record_count} records to {file_path}")
        
    except Exception as e:
        log.error(f"Failed to write CSV file {file_path}: {e}")
        raise


def write_csv(file_path: str, data: List[Dict]) -> None:
    """
    Write a list of dictionaries to a CSV file without schema (backward compatibility).
    Headers will be derived from the data keys.
    
    Args:
        file_path: Path where the CSV file should be written
        data: List of dictionaries containing the data to write
                
    Raises:
        Exception: If the file cannot be written
    """
    write_csv_with_schema(file_path, data, schema=None)
