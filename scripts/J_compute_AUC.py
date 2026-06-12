# -*- coding: utf-8 -*-
"""
Script to compute the Area Under the Curve of all metrics for all strategies for all timestamps.
"""

import json
import pandas as pd
from paris_orderbike.utils import auc_from_metrics_dict


FOLDER_DATA = "./data/processed/"
FOLDER_PLOT = "./plots/"
TIMESTAMPS = [
    "2021-01-01",
    "2023-05-17",
    "2023-10-01",
    "2024-01-15",
    "2024-04-04",
    "2024-08-22",
    "2024-12-22",
    "2025-06-02",
    "2026-01-28",
    "No",
]
RAND_TRIAL_NUMBER = 500
BUFF_SIZE = 400
METRIC_LIST = [
    "coverage",
    "directness",
    "betweenness",
    "closeness",
    "random",
    "road_hierarchy",
    "bikenet_hierarchy",
    "real",
]
EXP_DISC = False


def main():
    aucs = []
    for metric in METRIC_LIST:
        foldermet = FOLDER_DATA + f"bs_{BUFF_SIZE}_{metric}/"
        if metric == "random":
            for i in range(RAND_TRIAL_NUMBER):
                with open(foldermet + f"random_{i:03}/metrics_growth.json", "r") as f:
                    met_dict = json.load(f)
                auc_cov = auc_from_metrics_dict(
                    met_dict,
                    "coverage",
                    normalize_y=True,
                    yaxis_method="natural",
                    exp_discounting=EXP_DISC,
                    normalize_max_auc=False,
                )
                auc_dir = auc_from_metrics_dict(
                    met_dict,
                    "directness",
                    normalize_y=False,
                    max_comparison_y="one",
                    exp_discounting=EXP_DISC,
                    normalize_max_auc=False,
                )
                aucs.append([metric, i, auc_cov, auc_dir])
        else:
            with open(foldermet + "metrics_growth.json", "r") as f:
                met_dict = json.load(f)
            auc_cov = auc_from_metrics_dict(
                met_dict,
                "coverage",
                normalize_y=True,
                yaxis_method="natural",
                exp_discounting=EXP_DISC,
                normalize_max_auc=False,
            )
            auc_dir = auc_from_metrics_dict(
                met_dict,
                "directness",
                normalize_y=False,
                max_comparison_y="one",
                exp_discounting=EXP_DISC,
                normalize_max_auc=False,
            )
            aucs.append([metric, 0, auc_cov, auc_dir])
        # Save everything as JSON with Pandas Dataframe
        df_growth = pd.DataFrame(
            aucs,
            columns=[
                "Metric optimized",
                "Trial",
                "AUC of Coverage",
                "AUC of Directness",
            ],
        )
        savename = str(FOLDER_DATA) + "auc_table_growth"
        savename += ".json"
        df_growth.to_json(savename)


if __name__ == "__main__":
    main()
