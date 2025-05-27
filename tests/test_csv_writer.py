            filename = os.path.join(temp_dir, "test_output.csv")
            
            # Write CSV
            write_csv_with_schema(filename, data, schema)