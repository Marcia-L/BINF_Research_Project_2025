"""
Input:
- CSV files produced by compare_baseline_and_ssps_provinces.py

Output:
- Global map of predicted provinces changed, colored by province label.
- Pie chart of province-to-province transition proportion

Usage:
    python plot_transition_province.py
    
"""

import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from cartopy import crs as ccrs
from cartopy import feature as cfeature


province_order = [
    "BALT", 
    "TRHI", "TGYR", "TRLO", 
    "APLR", "BPLR", 
    "CTEM", "OTEM", "STEM", "MTEM",
]

colors = plt.cm.tab10.colors   # province color
province_color = {
    province: colors[i]
    for i, province in enumerate(province_order)
}

# province: str to int
province_dict = {   
    province: i
    for i, province in enumerate(province_order)
}   



def load_compared_df(ssp):
    compared_df = f"/data/gpfs/projects/punim2700/outputs/global_province_changes/ssp{ssp}_predicted_changed_provinces.csv"
    compared_df = pd.read_csv(compared_df)
    return compared_df

    

def plot_world_map_colored_by_province(ssp, compared_df):
    changed_df = compared_df[compared_df["changed"] == True].copy()
    
    # Accurate to 0.05 degrees
    changed_df["latitude"] = (changed_df["latitude"]/0.05).round()*0.05
    changed_df["longitude"] = (changed_df["longitude"]/0.05).round()*0.05
    changed_df["ssp_province_code"] = changed_df["ssp_provinces"].map(province_dict)

    # breakpoint()

    
    # build grid from data lon/lat
    lat_vals = np.sort(changed_df["latitude"].unique())
    lon_vals = np.sort(changed_df["longitude"].unique())

    grid = (changed_df.pivot_table(
        index="latitude", 
        columns="longitude", 
        values="ssp_province_code",
        aggfunc="first",
    ).reindex(index=lat_vals, 
              columns=lon_vals))

    province_cmap = ListedColormap([
        province_color[province] for province in province_order
    ])
    
    fig = plt.figure(figsize=(16, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())


    # surface grid
    ax.pcolormesh(
        lon_vals,
        lat_vals,
        grid.values,
        cmap=province_cmap,
        shading="nearest",
        transform=ccrs.PlateCarree(),
        rasterized=True,
        zorder=0,
    )


    # atla base
    ax.set_global()
    ax.add_feature(
        cfeature.NaturalEarthFeature("physical", "land", "10m"),
        lw=0.5,
        alpha=1,
        color="#EFEFDB",
        zorder=2,
    )
    ax.add_feature(cfeature.LAKES, lw=0.5, zorder=2)
    ax.add_feature(cfeature.RIVERS, zorder=2)
    ax.coastlines(resolution="10m", lw=0.5, zorder=2)


    # add legend: match color with province label
    legend_handles = [
        Patch(facecolor=province_color[province], label=province)
        for province in province_order
    ]
    
    ax.legend(
        handles=legend_handles,
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        frameon=False,
        title="SSP province",
    )


    # plot map
    ax.set_title(
        f"ssp{ssp} predicted province", 
        size=15,
        loc="left",
    )

    os.makedirs("../outputs/figures/global/map_colored_by_province/", exist_ok=True)
    
    fig.savefig(
        f"../outputs/figures/global/map_colored_by_province/ssp{ssp}_map_colored_by_province.png",
        dpi=300,
        bbox_inches="tight",
    )



def plot_transition_province(ssp, compared_df):
    changed_df = compared_df[compared_df["changed"] == True].copy()

    # create province-to-province transition column
    changed_df["transition"] = (
        changed_df["baseline_provinces"] 
        + " to " 
        + changed_df["ssp_provinces"]
    )
    
    transition_counts = changed_df["transition"].value_counts()
    transition_prop = transition_counts / transition_counts.sum()

    # the displayed transition proportion 
    min_prop = 0.03   
    major_counts = transition_counts[transition_prop >= min_prop].copy()
    minor_counts = transition_counts[transition_prop < min_prop]

    # Others: non-displayed transitions
    if len(minor_counts) > 0:
        major_counts.loc["Others"] = minor_counts.sum()

    
    fig, ax = plt.subplots(figsize=(6, 6))

    pie_colors = plt.cm.tab20(np.linspace(0, 1, len(major_counts)))   

    if "Others" in major_counts.index:   # set to grey
        pie_colors[-1] = [0.55, 0.55, 0.55, 1]

    ax.pie(
        major_counts.values,
        colors=pie_colors,
        startangle=90,
        counterclock=False,
        autopct=lambda p: f"{p:.1f}%"
    )

    ax.legend(
        major_counts.index,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
    )

    ax.set_title(f"ssp{ssp} transition composition")

    os.makedirs("../outputs/figures/global/global_transition_province", exist_ok=True)
    
    fig.savefig(
        f"../outputs/figures/global/global_transition_province/ssp{ssp}_transition_province.png",
        dpi=300,
        bbox_inches="tight",
    )


def main():
    for ssp in ["119", "126", "245", "370", "460", "585"]: 
        compared_df = load_compared_df(ssp)
        plot_world_map_colored_by_province(ssp, compared_df)
        plot_transition_province(ssp, compared_df)


if __name__ == "__main__":
    main()