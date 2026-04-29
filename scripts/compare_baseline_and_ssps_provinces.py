"""
Comparing projected provinces of SSPs with the baseline to find the changed area.

Usage:
    python compare_baseline_and_ssps_provinces.py

"""

import pandas as pd
import geopandas as gpd


def baseline_provinces():
    baseline_province = "/data/gpfs/projects/punim2700/outputs/global_province_predictions/baseline_predicted_provinces.csv"
    baseline_province = pd.read_csv(baseline_province)
    return baseline_province


def ssp_provinces(ssp):
    ssp_province = f"/data/gpfs/projects/punim2700/outputs/global_province_predictions/ssp{ssp}_predicted_provinces.csv"
    ssp_province = pd.read_csv(ssp_province)
    ssp_province = ssp_province.rename(columns={"predicted_provinces": "ssp_provinces"})
    return ssp_province


def match_nearest_provinces(baseline_province, ssp_province, ssp):
    baseline_gdf = gpd.GeoDataFrame(
        baseline_province,
        geometry=gpd.points_from_xy(
            baseline_province["longitude"],
            baseline_province["latitude"],
        ),
        crs="EPSG:4326"
    )
    ssp_gdf = gpd.GeoDataFrame(
        ssp_province,
        geometry=gpd.points_from_xy(
            ssp_province["longitude"],
            ssp_province["latitude"],
        ),
        crs="EPSG:4326"
    )
    
    baseline_gdf = baseline_gdf.to_crs("EPSG:3395")
    ssp_gdf = ssp_gdf.to_crs("EPSG:3395")

    matched = gpd.sjoin_nearest(
        baseline_gdf, 
        ssp_gdf,
        how="left",
        distance_col="distance"   
    )
    
    matched["changed"] = matched["baseline_provinces"] != matched["ssp_provinces"]
    
    matched = matched.to_crs("EPSG:4326")
    matched["longitude"] = matched.geometry.x
    matched["latitude"] = matched.geometry.y

    matched_df = matched[
        [
            "latitude",
            "longitude",
            "baseline_provinces",
            "ssp_provinces",
            "changed"
        ]
    ]
    
    # breakpoint()

    matched_df.to_csv(f"/data/gpfs/projects/punim2700/outputs/global_province_changes/ssp{ssp}_predicted_changed_provinces.csv", index=False)
    

def main():
    baseline_province = baseline_provinces()
    
    for ssp in ["119", "126", "245", "370", "460", "585"]: 
        ssp_province = ssp_provinces(ssp)
        match_nearest_provinces(baseline_province, ssp_province, ssp)     
        

if __name__ == "__main__":
    main()
