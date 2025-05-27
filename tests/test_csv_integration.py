"""
Integration tests for CSV utilities - testing cross-module functionality
Focus: Testing that the utils/csv_writer.py can be used by any module
"""

import os
import sys
import pytest
import tempfile
import csv

# Add the parent directory to the path so we can import the utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.csv_writer import write_csv, write_csv_with_schema
from utils.visualisations import create_visualization_csv


class TestCSVIntegration:
    """Integration tests for CSV utilities across different use cases"""

    def test_multiple_module_csv_workflow(self):
        """Test that multiple modules can use the CSV writer independently"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Simulate Module A (e.g., Azure topology)
            module_a_data = [
                {"resource_id": "vm-001", "type": "VirtualMachine", "location": "eastus"},
                {"resource_id": "db-002", "type": "Database", "location": "westus"}
            ]
            module_a_schema = ["resource_id", "type", "location"]
            
            filename_a = os.path.join(temp_dir, "module_a_resources.csv")
            write_csv_with_schema(filename_a, module_a_data, module_a_schema)
            
            # Simulate Module B (e.g., PowerBI)
            module_b_data = [
                {"workspace_id": "ws-123", "name": "Sales Workspace", "active": True},
                {"workspace_id": "ws-456", "name": "Marketing Workspace", "active": False}
            ]
            module_b_schema = ["workspace_id", "name", "active"]
            
            filename_b = os.path.join(temp_dir, "module_b_workspaces.csv")
            write_csv_with_schema(filename_b, module_b_data, module_b_schema)
            
            # Verify both files exist and have correct structure
            assert os.path.exists(filename_a)
            assert os.path.exists(filename_b)
            
            # Check Module A CSV
            with open(filename_a, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                assert reader.fieldnames == module_a_schema
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]["resource_id"] == "vm-001"
                assert rows[0]["type"] == "VirtualMachine"
            
            # Check Module B CSV
            with open(filename_b, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                assert reader.fieldnames == module_b_schema
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]["workspace_id"] == "ws-123"
                assert rows[0]["name"] == "Sales Workspace"

    def test_visualization_utility_csv_integration(self):
        """Test that visualization utilities can use CSV writer with various schemas"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test data representing different module outputs
            test_datasets = [
                {
                    "data": [
                        {"service": "webapp", "status": "running", "instances": 3},
                        {"service": "database", "status": "healthy", "instances": 1}
                    ],
                    "schema": ["service", "status", "instances"],
                    "filename": "services_summary.csv"
                },
                {
                    "data": [
                        {"metric": "cpu_usage", "value": 75.5, "threshold": 80},
                        {"metric": "memory_usage", "value": 60.2, "threshold": 85}
                    ],
                    "schema": ["metric", "value", "threshold"],
                    "filename": "performance_metrics.csv"
                }
            ]
            
            for dataset in test_datasets:
                filepath = os.path.join(temp_dir, dataset["filename"])
                
                # Simulate visualization utility using CSV writer
                create_visualization_csv(
                    data=dataset["data"],
                    filename=filepath,
                    schema=dataset["schema"]
                )
                
                # Verify file creation and structure
                assert os.path.exists(filepath)
                
                with open(filepath, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    assert reader.fieldnames == dataset["schema"]
                    rows = list(reader)
                    assert len(rows) == len(dataset["data"])

    def test_schema_flexibility_across_modules(self):
        """Test that different modules can use completely different schema formats"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Scenario 1: Simple flat schema
            simple_data = [{"id": 1, "name": "test"}]
            simple_schema = ["id", "name"]
            simple_file = os.path.join(temp_dir, "simple.csv")
            
            write_csv_with_schema(simple_file, simple_data, simple_schema)
            
            # Scenario 2: Complex schema with many fields
            complex_data = [
                {
                    "subscription_id": "sub-123",
                    "resource_group": "rg-prod",
                    "resource_name": "vm-web-01",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "location": "East US",
                    "sku": "Standard_D2s_v3",
                    "state": "Running",
                    "cost_per_month": 156.78,
                    "tags": "env:prod,team:web"
                }
            ]
            complex_schema = [
                "subscription_id", "resource_group", "resource_name", 
                "resource_type", "location", "sku", "state", 
                "cost_per_month", "tags"
            ]
            complex_file = os.path.join(temp_dir, "complex.csv")
            
            write_csv_with_schema(complex_file, complex_data, complex_schema)
            
            # Verify both work independently
            assert os.path.exists(simple_file)
            assert os.path.exists(complex_file)
            
            # Check simple CSV
            with open(simple_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                assert len(reader.fieldnames) == 2
                rows = list(reader)
                assert len(rows) == 1
            
            # Check complex CSV
            with open(complex_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                assert len(reader.fieldnames) == 9
                rows = list(reader)
                assert len(rows) == 1
                assert rows[0]["resource_name"] == "vm-web-01"

    def test_csv_writer_error_handling_integration(self):
        """Test that CSV writer handles various error scenarios gracefully"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test 1: Empty data with schema
            empty_data = []
            schema = ["field1", "field2"]
            empty_file = os.path.join(temp_dir, "empty.csv")
            
            # Should create file with headers even with no data
            write_csv_with_schema(empty_file, empty_data, schema)
            assert os.path.exists(empty_file)
            
            with open(empty_file, 'r', newline='', encoding='utf-8') as f:
                content = f.read()
                assert "field1,field2" in content
            
            # Test 2: Mismatched data fields (data has fields not in schema)
            mismatched_data = [
                {"expected_field": "value1", "extra_field": "unexpected"},
                {"expected_field": "value2", "another_extra": "also_unexpected"}
            ]
            mismatched_schema = ["expected_field"]
            mismatched_file = os.path.join(temp_dir, "mismatched.csv")
            
            # Should still work, only writing fields that are in schema
            write_csv_with_schema(mismatched_file, mismatched_data, mismatched_schema)
            assert os.path.exists(mismatched_file)
            
            with open(mismatched_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                assert reader.fieldnames == ["expected_field"]
                rows = list(reader)
                assert len(rows) == 2
                assert "extra_field" not in reader.fieldnames

    def test_backward_compatibility_integration(self):
        """Test that the old write_csv function still works alongside new functionality"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Old style usage
            old_data = [{"field1": "value1", "field2": "value2"}]
            old_file = os.path.join(temp_dir, "old_style.csv")
            
            write_csv(old_file, old_data)
            assert os.path.exists(old_file)
            
            # New style usage
            new_data = [{"field1": "value1", "field2": "value2"}]
            new_schema = ["field1", "field2"]
            new_file = os.path.join(temp_dir, "new_style.csv")
            
            write_csv_with_schema(new_file, new_data, new_schema)
            assert os.path.exists(new_file)
            
            # Both should produce valid CSV files
            for filepath in [old_file, new_file]:
                with open(filepath, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) == 1
                    assert rows[0]["field1"] == "value1"

    def test_cross_module_data_compatibility(self):
        """Test that data from one module can be processed by another module's schema"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Simulate data from Module A
            source_data = [
                {"id": "resource-123", "name": "web-server", "type": "vm", "region": "us-east"},
                {"id": "resource-456", "name": "database", "type": "sql", "region": "us-west"}
            ]
            
            # Module B wants to process this data with its own schema
            # (maybe it only cares about certain fields or wants different headers)
            module_b_schema = ["id", "name", "region"]  # Excludes 'type'
            
            processed_file = os.path.join(temp_dir, "processed_by_module_b.csv")
            write_csv_with_schema(processed_file, source_data, module_b_schema)
            
            assert os.path.exists(processed_file)
            
            with open(processed_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                assert reader.fieldnames == module_b_schema
                rows = list(reader)
                assert len(rows) == 2
                # Should have the fields Module B cares about
                assert rows[0]["id"] == "resource-123"
                assert rows[0]["name"] == "web-server"
                assert rows[0]["region"] == "us-east"
                # Should not have the 'type' field that Module B didn't include in schema
                assert "type" not in reader.fieldnames

    def test_utils_independence_verification(self):
        """Verify that utils can be used without importing any modules"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # This test should work without importing any modules at all
            # Only import the utils
            
            test_data = [
                {"utility_test": "value1", "independent": True},
                {"utility_test": "value2", "independent": True}
            ]
            test_schema = ["utility_test", "independent"]
            test_file = os.path.join(temp_dir, "utils_independence.csv")
            
            # Use the CSV writer directly
            write_csv_with_schema(test_file, test_data, test_schema)
            
            assert os.path.exists(test_file)
            
            with open(test_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                assert reader.fieldnames == test_schema
                rows = list(reader)
                assert len(rows) == 2
                assert all(row["independent"] == "True" for row in rows)
                
            # This proves the utility works independently of any module code