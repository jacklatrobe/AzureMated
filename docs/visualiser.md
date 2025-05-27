# Visualization Utilities

This document describes the helper functions found in `utils/visualisations.py`. These helpers use `networkx` and `matplotlib` to create diagrams that illustrate Azure management groups, subscriptions and resources.

## Available Functions

### `create_azure_topology_visualizations(output_dir, csv_schemas=None)`
Reads topology CSV files from `output_dir` and generates a series of PNG images showing the hierarchy. Returns `True` when the visualizations are created successfully.

### `create_mgmt_group_subscription_viz(mgmt_groups_df, subscriptions_df, output_dir)`
Creates a graph linking management groups to their subscriptions.

### `create_subscription_resource_group_viz(subscriptions_df, resource_groups_df, output_dir)`
Visualizes the relationship between subscriptions and resource groups.

### `create_resource_group_resources_viz(resource_groups_df, resources_df, output_dir)`
Aggregates resources by type inside each resource group and produces a diagram.

### `create_complete_hierarchy_viz(mgmt_groups_df, subscriptions_df, resource_groups_df, resources_df, output_dir)`
Combines all levels of topology into a single comprehensive hierarchy visualization.
