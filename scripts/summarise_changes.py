"""
Plot global map of predicted provinces from model output.

Input:
- CSV files produced by compare_baseline_and_ssps_provinces.py

Analysis:
- Changed proportion
- Area change of each province
- Proportion change of each province
- Stability ranking of provinces

Usage:
    python summarise_changes.py
    
"""

import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


province_order = [
    "BALT", 
    "TRHI", "TGYR", "TRLO", 
    "APLR", "BPLR", 
    "CTEM", "OTEM", "STEM", "MTEM",
]

ssp_title = {
        "119": "SSP1-1.9",
        "126": "SSP1-2.6",
        "245": "SSP2-4.5",
        "370": "SSP3-7.0",
        "460": "SSP4-6.0",
        "585": "SSP5-8.5",
    }

ssp_list = ["119", "126", "245", "370", "460", "585"]



def load_compared_df(ssp):
    compared_df = f"/data/gpfs/projects/punim2700/outputs/global_province_changes/ssp{ssp}_predicted_changed_provinces.csv"
    compared_df = pd.read_csv(compared_df)
    return compared_df


def calculate_cell_area_km2(compared_df):
    R = 6371.0
    dlat = 0.05
    dlon = 0.05

    lat_lower = np.deg2rad(compared_df["latitude"] - dlat / 2)
    lat_upper = np.deg2rad(compared_df["latitude"] + dlat / 2)
    dlon_rad = np.deg2rad(dlon)

    compared_df["cell_area_km2"] = R**2 * dlon_rad * (np.sin(lat_upper) - np.sin(lat_lower))

    return compared_df


def summarise_area_change(ssp_list):
    summary_rows = []

    for ssp in ssp_list:
        compared_df = load_compared_df(ssp)

        total_points = len(compared_df)
        changed_points = compared_df["changed"].sum()
        changed_percent = changed_points / total_points * 100

        summary_rows.append({
            "ssp": ssp,
            "total_points": total_points,
            "changed_points": changed_points,
            "changed_percent": changed_percent.round(3)
        })

    summary_df = pd.DataFrame(summary_rows)

    os.makedirs("../outputs/tables/global_summary", exist_ok=True)
    summary_df.to_csv("../outputs/tables/global_summary/global_area_change_summary.csv", index=False)
    
    return summary_df


def plot_area_change_proportion(summary_df):
    os.makedirs("../outputs/figures/global_changed_areas", exist_ok=True)
    
    for _, row in summary_df.iterrows():
        ssp = str(int(row["ssp"]))
        total_points = row["total_points"]
        changed_points = row["changed_points"]
        unchanged_points = total_points - changed_points

        fig, ax = plt.subplots(figsize=(5,5))

        ax.pie(
            [changed_points, unchanged_points],
            colors=["#6f8fc2", "#f2f2f2"],
            startangle=90,
            counterclock=False,
            autopct=lambda p: f"{p:.0f}%" if p < 50 else "",
        )
        ax.set_title(ssp_title[ssp])
        
        fig.savefig(
            f"../outputs/figures/global_changed_areas/ssp{ssp}_changed_proportion_pie.png",
            dpi=300,
            bbox_inches="tight",
    )


def summarise_province_area_change(ssp_list):
    summary_rows = []

    for ssp in ssp_list:
        compared_df = load_compared_df(ssp)
        compared_df = calculate_cell_area_km2(compared_df)

        total_area_km2 = compared_df["cell_area_km2"].sum()

        for province in province_order:
            baseline_area_km2 = compared_df.loc[
                compared_df["baseline_provinces"] == province,
                "cell_area_km2"
            ].sum()

            ssp_area_km2 = compared_df.loc[
                compared_df["ssp_provinces"] == province,
                "cell_area_km2"
            ].sum()

            area_change_km2 = ssp_area_km2 - baseline_area_km2

            baseline_percent = baseline_area_km2 / total_area_km2 * 100
            ssp_percent = ssp_area_km2 / total_area_km2 * 100
            percent_change = ssp_percent - baseline_percent

            summary_rows.append({
                "ssp": ssp,
                "province": province,
                "baseline_area_km2": baseline_area_km2.round(2),
                "ssp_area_km2": ssp_area_km2.round(2),
                "area_change_km2": area_change_km2.round(2),
                "baseline_percent": baseline_percent.round(3),
                "ssp_percent": ssp_percent.round(3),
                "percent_change": percent_change.round(3),
            })

    summary_df = pd.DataFrame(summary_rows)
    
    os.makedirs("../outputs/tables/global_summary", exist_ok=True)
    summary_df.to_csv("../outputs/tables/global_summary/province_area_change_summary.csv", index=False)
    
    return summary_df
            

def plot_province_area_change_proportion(summary_df):
    os.makedirs("../outputs/figures/province_proportion_change", exist_ok=True)
    
    for ssp in ssp_list:
        ssp_df = summary_df[summary_df["ssp"].astype(str) == ssp]
        ssp_df = ssp_df.set_index("province").loc[province_order].reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.bar(
            ssp_df["province"],
            ssp_df["percent_change"],
        )

        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(ssp_title[ssp])
        ax.set_xlabel("Province")
        ax.set_ylabel("Proportion change (%)")
        ax.tick_params(axis="x", rotation=45)

        fig.savefig(
        f"../outputs/figures/province_proportion_change/ssp{ssp}_province_proportion_change_bar.png",
        dpi=300,
        bbox_inches="tight",
    )


def build_transition_matrix_count(ssp_list):
    os.makedirs("../outputs/tables/global_transition_matrix", exist_ok=True)
    
    for ssp in ssp_list:
        compared_df = load_compared_df(ssp)

        trans_mat = pd.crosstab(
            compared_df["baseline_provinces"],
            compared_df["ssp_provinces"]
        )

        trans_mat = trans_mat.reindex(
            index = province_order,
            columns = province_order,
            fill_value = 0
        )
        
        # breakpoint()

        trans_mat.to_csv(f"../outputs/tables/global_transition_matrix/ssp{ssp}_transition_matrix_count.csv")


def build_transition_matrix_proportion(ssp_list):
    os.makedirs("../outputs/tables/global_transition_matrix", exist_ok=True)
    
    for ssp in ssp_list:
        compared_df = load_compared_df(ssp)

        trans_prop = pd.crosstab(
            compared_df["baseline_provinces"],
            compared_df["ssp_provinces"],
            normalize = "index"
        )

        trans_prop = trans_prop.reindex(
            index = province_order,
            columns = province_order,
            fill_value = 0
        )

        trans_prop = trans_prop.round(3)

        # breakpoint()

        trans_prop.to_csv(f"../outputs/tables/global_transition_matrix/ssp{ssp}_transition_matrix_proportion.csv")



def main():
    # global scale change summary
    area_changed_df = summarise_area_change(ssp_list)
    plot_area_change_proportion(area_changed_df)

    # province scale change summary
    province_area_changed_df = summarise_province_area_change(ssp_list)
    plot_province_area_change_proportion(province_area_changed_df)

    # transition matrix 
    build_transition_matrix_count(ssp_list)
    build_transition_matrix_proportion(ssp_list)
        

if __name__ == "__main__":
    main()