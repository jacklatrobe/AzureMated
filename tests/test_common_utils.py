"""
Tests for the common.py utilities
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.common import format_table, display_results


class TestCommonUtils:
    """Test class for common.py utilities"""

    def test_format_table_with_data(self):
        """Test that format_table correctly formats data into a rich table"""
        # Sample data
        data = [
            {"id": "1", "name": "Test Item 1", "status": "Active"},
            {"id": "2", "name": "Test Item 2", "status": "Inactive"}
        ]
        
        # Column definitions
        columns = {
            "id": "ID",
            "name": "Name",
            "status": "Status"
        }
        
        # Call the function
        table = format_table(data, "Test Table", columns)
        
        # Verify the table properties
        assert table.title == "Test Table"
        assert len(table.columns) == 3
        assert table.columns[0].header == "ID"
        assert table.columns[1].header == "Name"
        assert table.columns[2].header == "Status"
        
        # Rich Table doesn't expose rows directly, so we can't easily test the row content
        # But we can test that the table was created successfully

    def test_format_table_with_missing_data(self):
        """Test that format_table handles missing data gracefully"""
        # Sample data with missing fields
        data = [
            {"id": "1", "name": "Test Item 1"},  # Missing status
            {"id": "2", "status": "Inactive"}   # Missing name
        ]
        
        # Column definitions
        columns = {
            "id": "ID",
            "name": "Name",
            "status": "Status"
        }
        
        # Call the function
        table = format_table(data, "Test Table", columns)
        
        # Verify the table properties
        assert table.title == "Test Table"
        assert len(table.columns) == 3
        
        # The function should fill missing values with empty strings

    def test_display_results_with_data(self):
        """Test that display_results correctly displays a table when data is present"""
        # Sample data
        data = [
            {"id": "1", "name": "Test Item 1", "status": "Active"},
            {"id": "2", "name": "Test Item 2", "status": "Inactive"}
        ]
        
        # Column definitions
        columns = {
            "id": "ID",
            "name": "Name",
            "status": "Status"
        }
        
        # Mock the console.print function
        with patch('utils.common.console.print') as mock_print:
            # Call the function
            display_results(data, "Test Table", columns)
            
            # Verify console.print was called
            mock_print.assert_called_once()
            
            # The argument should be a Table object
            args, _ = mock_print.call_args
            assert args[0].title == "Test Table"

    def test_display_results_with_empty_data(self):
        """Test that display_results shows a message when no data is present"""
        # Empty data
        data = []
        
        # Column definitions
        columns = {
            "id": "ID",
            "name": "Name",
            "status": "Status"
        }
        
        # Mock the console.print function
        with patch('utils.common.console.print') as mock_print:
            # Call the function
            display_results(data, "Test Items", columns)
            
            # Verify console.print was called with the correct message
            mock_print.assert_called_once_with("[yellow]No test items found[/yellow]")
