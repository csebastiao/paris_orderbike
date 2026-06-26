# -*- coding: utf-8 -*-
"""
Script to compute the Area Under the Curve of all metrics for all strategies for all timestamps.
"""

import json
import pandas as pd
from paris_orderbike.utils import auc_from_metrics_dict
from G_grow_bikenet import (
    BUFF_SIZE,
    NUM_HIER_TRIAL,
    NUM_RAND_TRIAL,
    NUM_COV_TRIAL,
    FOLDEROOT,
    END_FOLDERS,
)

METRIC_LIST = [
    "coverage",
    "directness",
    "betweenness",
    "dual_betweenness",
    "closeness",
    "dual_closeness",
    "random",
    "road_hierarchy",
    "road_hierarchy_coverage",
    "road_hierarchy_directness",
    "real",
]
EXP_DISC = False


def main():
    for end_folder in END_FOLDERS:
        folder_data = FOLDEROOT + end_folder + "/"
        aucs = []
        for met in METRIC_LIST:
            foldermet = folder_data + f"bs_{BUFF_SIZE}_{met}/"
            if met in ["random", "road_hierarchy", "bikenet_hierarchy", "coverage"]:
                if met == "random":
                    num_step = NUM_RAND_TRIAL
                elif met in ["road_hierarchy", "bikenet_hierarchy"]:
                    num_step = NUM_HIER_TRIAL
                elif met in ["coverage"]:
                    num_step = NUM_COV_TRIAL
                for i in range(num_step):
                    with open(
                        foldermet + f"{met}_{i:03}/metrics_growth.json", "r"
                    ) as f:
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
                    aucs.append([met, i, auc_cov, auc_dir])
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
                aucs.append([met, 0, auc_cov, auc_dir])
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
            savename = str(folder_data) + "auc_table_growth"
            savename += ".json"
            df_growth.to_json(savename)


if __name__ == "__main__":
    main()
