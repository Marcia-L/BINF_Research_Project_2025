"""
Driver attribution map visualisation

Reads the per-SSP driver z-score CSVs produced by compute_zscore.py and generates:
- 6-panel driver map (one panel per SSP), each grid cell coloured by dominant driver
- 2-panel comparison map for the two extreme scenarios (SSP1-1.9 vs SSP5-8.5)
- summary bar chart of the percentage of transitioning area attributed to each dominant driver, per SSP

Usage:
    python plot_driver_maps.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
import cartopy.feature as cfeature


driver_zscores_path = "/data/gpfs/projects/punim2700/outputs/driver_attribution"
output_path = "/data/gpfs/projects/punim2700/outputs/figures/driver_maps"

ssp_list = ["119", "126", "245", "370", "460", "585"]
ssp_labels = {
    "119": "SSP1-1.9", "126": "SSP1-2.6", "245": "SSP2-4.5",
    "370": "SSP3-7.0", "460": "SSP4-6.0", "585": "SSP5-8.5",
}


predictor_list = [
    "Chlorophyll", "DissolvedIron", "DissolvedMolecularOxygen", "Nitrate",
    "OceanTemperature", "Phosphate", "Salinity", "SeaIceCover", "Silicate", "pH",
]



def build_driver_color_map(predictor_list):
    cmap = plt.get_cmap("tab10")
    return {var: cmap(i % 10) for i, var in enumerate(predictor_list)}


def load_driver_df(ssp):
    path = f"{driver_zscores_path}/driver_zscores_ssp{ssp}.csv"
    return pd.read_csv(path, index_col=0)



# base map layer forone SSP panel
def plot_single_panel(ax, df, color_map, title):
    ax.add_feature(cfeature.LAND, facecolor="lightgrey", zorder=0)
    ax.coastlines(linewidth=0.3)
    for var, color in color_map.items():
        sub = df[df["dominant_driver"] == var]
        if len(sub) == 0:
            continue
        ax.scatter(
            sub["longitude"], sub["latitude"],
            color=color, s=1, transform=ccrs.PlateCarree(),
            label=var, rasterized=True,
        )
    ax.set_title(title, fontsize=10)



# 6-panel driver map (one panel per SSP)
def plot_six_panel_driver_map(color_map):
    fig, axes = plt.subplots(
        3, 2, figsize=(12, 14), subplot_kw={"projection": ccrs.PlateCarree()},
    )
    axes = axes.flatten()

    for ax, ssp in zip(axes, ssp_list):
        df = load_driver_df(ssp)
        plot_single_panel(ax, df, color_map, ssp_labels[ssp])

    handles = [mpatches.Patch(color=c, label=v) for v, c in color_map.items()]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=8, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Dominant environmental driver of predicted province transitions", fontsize=13)
    fig.tight_layout(rect=[0, 0.04, 1, 0.97])

    out_path = f"{output_path}/driver_map_all_ssp.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)



# 2-panel extreme comparison map (ssp119 vs ssp585)
def plot_extreme_comparison(color_map):
    fig, axes = plt.subplots(
        1, 2, figsize=(14, 6), subplot_kw={"projection": ccrs.PlateCarree()},
    )

    for ax, ssp in zip(axes, ["119", "585"]):
        df = load_driver_df(ssp)
        plot_single_panel(ax, df, color_map, ssp_labels[ssp])

    handles = [mpatches.Patch(color=c, label=v) for v, c in color_map.items()]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=9, bbox_to_anchor=(0.5, -0.05))
    fig.suptitle("Dominant environmental driver: low- vs high-emission scenario", fontsize=13)
    fig.tight_layout(rect=[0, 0.06, 1, 0.95])

    out_path = f"{output_path}/driver_map_ssp119_vs_ssp585.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# summary bar chart
def compute_driver_summary(color_map):
    records = []
    for ssp in ssp_list:
        df = load_driver_df(ssp)
        total = len(df)
        counts = df["dominant_driver"].value_counts()
        for var in predictor_list:
            pct = (counts.get(var, 0) / total * 100) if total > 0 else 0
            records.append({"ssp": ssp, "driver": var, "percent": pct})
    return pd.DataFrame(records)



def plot_driver_summary_bar_chart(color_map):
    summary_df = compute_driver_summary(color_map)

    # fix row/column order to match colour map
    pivot = summary_df.pivot(index="ssp", columns="driver", values="percent")
    pivot = pivot.reindex(ssp_list)[predictor_list]   
    

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = pd.Series([0.0] * len(pivot), index=pivot.index)
    for var in predictor_list:
        ax.bar(
            [ssp_labels[s] for s in pivot.index],
            pivot[var],
            bottom=bottom,
            color=color_map[var],
            label=var,
        )
        bottom += pivot[var].fillna(0)

    ax.set_ylabel("Percentage of transitioning area (%)")
    ax.set_title("Dominant driver attribution by SSP")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8)
    fig.tight_layout()

    out_path = f"{output_path}/driver_summary_bar_chart.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)



def main():
    os.makedirs(output_path, exist_ok=True)
    color_map = build_driver_color_map(predictor_list)
    plot_six_panel_driver_map(color_map)
    plot_extreme_comparison(color_map)
    plot_driver_summary_bar_chart(color_map)


if __name__ == "__main__":
    main()