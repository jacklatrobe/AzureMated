"""
Reports Module

This module assembles existing module output files into a single HTML report.
It does not query Azure services. Instead it reads CSV files produced by other
modules and, if present, converts them into HTML tables and embeds any
visualisation images found in the output directory.

Module Structure for Module Loader Compatibility:
-------------------------------------------------
1. Defines a `run` function at the module level as the entry point.
2. Accepts `subscription_id` and additional parameters for compatibility.
3. Returns a dictionary with the result of the operation.
"""

from __future__ import annotations

import os
import logging
from typing import Optional, Dict, List

import pandas as pd

log = logging.getLogger("fabric_friend")


class ReportsManager:
    """Manager class to generate HTML reports from existing data files."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def _load_csv(self, filename: str) -> Optional[pd.DataFrame]:
        path = os.path.join(self.output_dir, filename)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                return pd.read_csv(path)
            except Exception as e:  # pragma: no cover - unexpected read error
                log.warning(f"Failed to load CSV {filename}: {e}")
        return None

    def _add_section(self, parts: List[str], title: str, df: pd.DataFrame) -> None:
        parts.append(f"<h2>{title}</h2>")
        parts.append(df.to_html(index=False))

    def build_report(self) -> str:
        """Generate the HTML report file and return its path."""
        parts: List[str] = [
            "<html>",
            "<head><title>FabricFriend Report</title></head>",
            "<body>",
            "<h1>FabricFriend Report</h1>",
        ]

        # Topology CSV files
        topology_files: Dict[str, str] = {
            "Subscriptions": "subscriptions.csv",
            "Management Groups": "management_groups.csv",
            "Resource Groups": "resource_groups.csv",
            "Resources": "resources.csv",
        }
        for title, fname in topology_files.items():
            df = self._load_csv(fname)
            if df is not None and not df.empty:
                self._add_section(parts, title, df)

        # Topology visualisations if present
        for img in [
            "mgmt_groups_subscriptions.png",
            "subscriptions_resource_groups.png",
            "resource_groups_resources.png",
            "complete_azure_hierarchy.png",
        ]:
            path = os.path.join(self.output_dir, img)
            if os.path.exists(path):
                parts.append(f'<img src="{img}" alt="{img}" style="max-width: 100%;">')

        # Power BI CSV files
        powerbi_files: Dict[str, str] = {
            "Capacities": "capacities.csv",
            "Workspaces": "workspaces.csv",
            "Workspace Users": "workspace_users.csv",
            "Dashboards": "dashboards.csv",
            "Dataflows": "dataflows.csv",
            "Datasets": "datasets.csv",
        }
        for title, fname in powerbi_files.items():
            df = self._load_csv(fname)
            if df is not None and not df.empty:
                self._add_section(parts, title, df)

        parts.append("</body></html>")

        os.makedirs(self.output_dir, exist_ok=True)
        report_path = os.path.join(self.output_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))

        return report_path


def run(subscription_id: Optional[str] = None, output_dir: str = "./outputs", **kwargs) -> Dict[str, str]:
    """Entry point for the reports module used by the module loader."""
    from utils import console

    console.print("[blue]Generating HTML report...[/blue]")
    manager = ReportsManager(output_dir)
    report_path = manager.build_report()
    console.print(f"[green]Report generated at {report_path}[/green]")
    return {"status": "success", "report": report_path}
