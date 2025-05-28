"""Tests for the reports module"""

import os
import sys
import csv
import tempfile

# Add repository root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.module_loader import load_and_run


def create_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


class TestReportsModule:
    def test_generate_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample topology csv
            create_csv(
                os.path.join(temp_dir, "subscriptions.csv"),
                ["subscription_id", "display_name"],
                [{"subscription_id": "sub1", "display_name": "Test Sub"}],
            )
            # Create a fake visualization image
            with open(os.path.join(temp_dir, "mgmt_groups_subscriptions.png"), "wb") as f:
                f.write(b"fake")

            result = load_and_run("modules.reports", {"output_dir": temp_dir})
            assert result["status"] == "success"
            report_file = os.path.join(temp_dir, "report.html")
            assert os.path.exists(report_file)
            content = open(report_file, "r", encoding="utf-8").read()
            assert "Test Sub" in content
