"""Tests for the visualization utilities"""

import os
import sys
import tempfile

import pandas as pd
import matplotlib
matplotlib.use("Agg")

# Add repo root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.visualisations import (
    create_mgmt_group_subscription_viz,
    create_subscription_resource_group_viz,
    create_resource_group_resources_viz,
    create_complete_hierarchy_viz,
    create_azure_topology_visualizations,
)

from unittest.mock import patch


class TestVisualizationUtilities:
    """Test suite for utils.visualisations"""

    def test_create_mgmt_group_subscription_viz(self):
        mgmt_df = pd.DataFrame([
            {"id": "mg1", "name": "mg1", "display_name": "MG", "tenant_id": "t", "type": "mg"}
        ])
        subs_df = pd.DataFrame([
            {"subscription_id": "sub1", "display_name": "Sub"}
        ])
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("utils.visualisations.plt.savefig") as mock_save:
                with patch("utils.console.print"):
                    create_mgmt_group_subscription_viz(mgmt_df, subs_df, temp_dir)
                file_path = os.path.join(temp_dir, "mgmt_groups_subscriptions.png")
                mock_save.assert_called_once()
                assert mock_save.call_args[0][0] == file_path

    def test_create_subscription_resource_group_viz(self):
        subs_df = pd.DataFrame([
            {"subscription_id": "sub1", "display_name": "Sub"}
        ])
        rgs_df = pd.DataFrame([
            {"id": "rg1", "name": "RG", "subscription_id": "sub1"}
        ])
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("utils.visualisations.plt.savefig") as mock_save:
                with patch("utils.console.print"):
                    create_subscription_resource_group_viz(subs_df, rgs_df, temp_dir)
                file_path = os.path.join(temp_dir, "subscriptions_resource_groups.png")
                mock_save.assert_called_once()
                assert mock_save.call_args[0][0] == file_path

    def test_create_resource_group_resources_viz(self):
        rgs_df = pd.DataFrame([
            {"id": "rg1", "name": "RG"}
        ])
        resources_df = pd.DataFrame([
            {"resource_group": "RG", "type": "vm"},
            {"resource_group": "RG", "type": "vm"},
        ])
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("utils.visualisations.plt.savefig") as mock_save:
                with patch("utils.console.print"):
                    create_resource_group_resources_viz(rgs_df, resources_df, temp_dir)
                file_path = os.path.join(temp_dir, "resource_groups_resources.png")
                mock_save.assert_called_once()
                assert mock_save.call_args[0][0] == file_path

    def test_create_complete_hierarchy_viz(self):
        mgmt_df = pd.DataFrame([
            {"id": "mg1", "name": "mg1", "display_name": "MG", "tenant_id": "t", "type": "mg"}
        ])
        subs_df = pd.DataFrame([
            {"subscription_id": "sub1", "display_name": "Sub"}
        ])
        rgs_df = pd.DataFrame([
            {"id": "rg1", "name": "RG", "subscription_id": "sub1"}
        ])
        resources_df = pd.DataFrame([
            {"resource_group": "RG", "type": "vm"}
        ])
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("utils.visualisations.plt.savefig") as mock_save:
                with patch("utils.console.print"):
                    create_complete_hierarchy_viz(mgmt_df, subs_df, rgs_df, resources_df, temp_dir)
                file_path = os.path.join(temp_dir, "complete_azure_hierarchy.png")
                mock_save.assert_called_once()
                assert mock_save.call_args[0][0] == file_path

    def test_create_azure_topology_visualizations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mgmt_df = pd.DataFrame([
                {"id": "mg1", "name": "mg1", "display_name": "MG", "tenant_id": "t", "type": "mg"}
            ])
            subs_df = pd.DataFrame([
                {"subscription_id": "sub1", "display_name": "Sub"}
            ])
            rgs_df = pd.DataFrame([
                {"id": "rg1", "name": "RG", "subscription_id": "sub1"}
            ])
            resources_df = pd.DataFrame([
                {"resource_group": "RG", "type": "vm"}
            ])

            mgmt_df.to_csv(os.path.join(temp_dir, "management_groups.csv"), index=False)
            subs_df.to_csv(os.path.join(temp_dir, "subscriptions.csv"), index=False)
            rgs_df.to_csv(os.path.join(temp_dir, "resource_groups.csv"), index=False)
            resources_df.to_csv(os.path.join(temp_dir, "resources.csv"), index=False)

            with (
                patch("utils.visualisations.create_mgmt_group_subscription_viz") as m1,
                patch("utils.visualisations.create_subscription_resource_group_viz") as m2,
                patch("utils.visualisations.create_resource_group_resources_viz") as m3,
                patch("utils.visualisations.create_complete_hierarchy_viz") as m4,
                patch("utils.console.print")
            ):
                result = create_azure_topology_visualizations(temp_dir)
                assert result is True
                m1.assert_called_once()
                m2.assert_called_once()
                m3.assert_called_once()
                m4.assert_called_once()
