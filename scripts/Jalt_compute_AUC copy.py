"""
Script to compute the Area Under the Curve of all metrics for all strategies for all timestamps.
"""

import json

import pandas as pd
from Ga_grow_bikenet import (
    END_FOLDERS,
    FOLDEROOT,
    NUM_COV_TRIAL,
    NUM_HIER_TRIAL,
    NUM_RAND_TRIAL,
)
from I_grow_random_real_bikenet import NUM_RAND_REAL_TRIAL

from paris_orderbike.utils import auc_from_metrics_dict

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
    "real_random",
    # Only for 400
    "random_disconnected",
    "random_relaxed",
]
EXP_GAP = 10


def main():
    for exp_disc in [
        True,
        False,
    ]:
        for buffer_size in [
            # 100,
            # 200,
            # 300,
            400,
            # 500,
            # 600,
            # 700,
            # 800
        ]:
            for end_folder in END_FOLDERS:
                folder_data = FOLDEROOT + end_folder + "/"
                aucs = []
                for met in METRIC_LIST:
                    foldermet = folder_data + f"bs_{buffer_size}_{met}/"
                    if met in [
                        "random",
                        "random_disconnected",
                        "random_relaxed",
                        "road_hierarchy",
                        "bikenet_hierarchy",
                        "coverage",
                    ]:
                        if met in ["random", "random_disconnected", "random_relaxed"]:
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
                                exp_discounting=exp_disc,
                                exp_gap=EXP_GAP,
                                normalize_max_auc=False,
                            )
                            auc_dir = auc_from_metrics_dict(
                                met_dict,
                                "directness",
                                normalize_y=False,
                                max_comparison_y="one",
                                exp_discounting=exp_disc,
                                exp_gap=EXP_GAP,
                                normalize_max_auc=False,
                            )
                            auc_gin = auc_from_metrics_dict(
                                met_dict,
                                "gini",
                                normalize_y=False,
                                max_comparison_y="one",
                                exp_discounting=exp_disc,
                                exp_gap=EXP_GAP,
                                normalize_max_auc=False,
                            )
                            aucs.append([met, i, auc_cov, auc_dir, auc_gin])
                    elif met == "real_random":
                        df_concat = pd.DataFrame()
                        for i in range(NUM_RAND_REAL_TRIAL):
                            df = pd.read_json(
                                foldermet + f"{met}_{i:03}/metrics_growth.json"
                            )
                            df_concat = pd.concat([df_concat, df])
                        df_avg = pd.DataFrame(average_x(df_concat))
                        met_real_random_dict = df_avg.to_dict(orient="list")
                        auc_cov = auc_from_metrics_dict(
                            met_real_random_dict,
                            "coverage",
                            normalize_y=True,
                            yaxis_method="natural",
                            exp_discounting=exp_disc,
                            exp_gap=EXP_GAP,
                            normalize_max_auc=False,
                        )
                        auc_dir = auc_from_metrics_dict(
                            met_real_random_dict,
                            "directness",
                            normalize_y=False,
                            max_comparison_y="one",
                            exp_discounting=exp_disc,
                            exp_gap=EXP_GAP,
                            normalize_max_auc=False,
                        )
                        auc_gin = auc_from_metrics_dict(
                            met_dict,
                            "gini",
                            normalize_y=False,
                            max_comparison_y="one",
                            exp_discounting=exp_disc,
                            exp_gap=EXP_GAP,
                            normalize_max_auc=False,
                        )
                        aucs.append([met, 0, auc_cov, auc_dir, auc_gin])
                    else:
                        with open(foldermet + "metrics_growth.json", "r") as f:
                            met_dict = json.load(f)
                        auc_cov = auc_from_metrics_dict(
                            met_dict,
                            "coverage",
                            normalize_y=True,
                            yaxis_method="natural",
                            exp_discounting=exp_disc,
                            exp_gap=EXP_GAP,
                            normalize_max_auc=False,
                        )
                        auc_dir = auc_from_metrics_dict(
                            met_dict,
                            "directness",
                            normalize_y=False,
                            max_comparison_y="one",
                            exp_discounting=exp_disc,
                            exp_gap=EXP_GAP,
                            normalize_max_auc=False,
                        )
                        auc_gin = auc_from_metrics_dict(
                            met_dict,
                            "gini",
                            normalize_y=False,
                            max_comparison_y="one",
                            exp_discounting=exp_disc,
                            exp_gap=EXP_GAP,
                            normalize_max_auc=False,
                        )
                        aucs.append([met, 0, auc_cov, auc_dir, auc_gin])
                    # Save everything as JSON with Pandas Dataframe
                    df_growth = pd.DataFrame(
                        aucs,
                        columns=[
                            "Metric optimized",
                            "Trial",
                            "AUC of Coverage",
                            "AUC of Directness",
                            "AUC of Gini",
                        ],
                    )
                savename = str(folder_data) + f"auc_table_growth_bs_{buffer_size}_alt"
                if exp_disc:
                    savename += f"_ed_{EXP_GAP}"
                savename += ".json"
                df_growth.to_json(savename)


def average_x(df):
    arr = []
    for ind in set(df.index):
        arr.append(df[df.index == ind].mean())
    return arr


if __name__ == "__main__":
    main()
