"""
Plot global map of predicted provinces from model output.

Input:
- CSV files produced by calculate_province_area_projections_.py

Usage:
    python map_world_atlas.py
    
"""

import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from cartopy import crs as ccrs
from cartopy import feature as cfeature



def plot_changed_map(ssp):
    compared_df = f"/data/gpfs/projects/punim2700/outputs/global_province_changes/ssp{ssp}_predicted_changed_provinces.csv"
    compared_df = pd.read_csv(compared_df)
    changed_df = compared_df[compared_df["changed"] == True].copy()

    
    # Accurate to 0.05 degrees
    changed_df["latitude"] = (changed_df["latitude"]/0.05).round()*0.05
    changed_df["longitude"] = (changed_df["longitude"]/0.05).round()*0.05
    changed_df["changed"] = 1
    

    # build grid from data lon/lat
    lat_vals = np.sort(changed_df["latitude"].unique())
    lon_vals = np.sort(changed_df["longitude"].unique())

    # breakpoint()

    grid = (changed_df.pivot_table(
        index="latitude", 
        columns="longitude", 
        values="changed",
        aggfunc="first",
    ).reindex(index=lat_vals, 
              columns=lon_vals))
    
    fig = plt.figure(figsize=(16, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())


    # surface grid
    ax.pcolormesh(
        lon_vals,
        lat_vals,
        grid.values,
        cmap=ListedColormap(["#6f8fc2"]),
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


    # plot map
    ax.set_title(
        f"{ssp} changed area", 
        size=15,
        loc="left",
    )

    os.makedirs("../outputs/figures", exist_ok=True)
    
    fig.savefig(
        f"../outputs/figures/global_changed_areas/ssp{ssp}_changed_area.png",
        dpi=300,
        bbox_inches="tight",
    )


def main():
    for ssp in ["119", "126", "245", "370", "460", "585"]: 
        plot_changed_map(ssp)


if __name__ == "__main__":
    main()
