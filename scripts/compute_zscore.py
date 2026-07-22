"""
Z-score driver attribution

Computes the z-score for each cell for all 6 SSPs and label the dominant environmental driving variable for each changed grid cell.

Usage:
    python compute_zscore.py

"""

import os
import pandas as pd
import xarray as xr
import numpy as np
import geopandas as gpd



sample_baseline_path = "/data/gpfs/projects/punim2700/data/share/sample_scenarios/baseline_samples.csv"
baseline_env_path = "/data/gpfs/projects/punim2700/data/share/global_scenarios/baseline_env_data.nc"
ssp_env_path = "/data/gpfs/projects/punim2700/data/share/global_scenarios"
changed_provinces_path = "/data/gpfs/projects/punim2700/outputs/global_province_changes"
output_path = "/data/gpfs/projects/punim2700/outputs/driver_attribution"



columns_to_remove_10var = ['DiffuseAttenuationCoefficientPAR', 'MixedLayerDepth', 'SeaWaterSpeed', 'PhotosyntheticallyAvailableRadiation', 'Terrain',
                         'AirTemperature', 'SeaIceThickness', 'TotalCloudFraction', 'TotalPhytoplankton']
columns_to_remove_9var = ['DiffuseAttenuationCoefficientPAR', 'MixedLayerDepth', 'SeaWaterSpeed', 'PhotosyntheticallyAvailableRadiation', 'Terrain',
                         'AirTemperature', 'SeaIceThickness', 'TotalCloudFraction', 'TotalPhytoplankton', 'Nitrate']



ssp_list = ["119", "126", "245", "370", "460", "585"]



def get_predictor_columns(ssp):
    sample_baseline = pd.read_csv(sample_baseline_path, index_col=0)
    columns_to_remove = columns_to_remove_9var if ssp == "245" else columns_to_remove_10var
    predictor_columns = sample_baseline.drop(columns_to_remove, axis=1).columns.tolist()
    return predictor_columns



def compute_present_day_stats(predictor_columns):
    baseline_env = xr.open_dataset(baseline_env_path)
    
    # compute mean & sd across present-day gred cells
    present_mean = {}
    present_std = {}
    for var in predictor_columns:
        present_mean[var] = float(baseline_env[var].mean(skipna=True))
        present_std[var] = float(baseline_env[var].std(skipna=True))

    return present_mean, present_std



def load_future_df(ssp, predictor_columns):
    # load future environmental data
    future_df = xr.open_dataset(f"{ssp_env_path}/ssp{ssp}_env_data.nc")

    future_df = future_df[predictor_columns].to_dataframe().reset_index()
    future_df = future_df[["latitude", "longitude"] + predictor_columns]
    future_df = future_df.dropna()

    return future_df



def load_compared_df(ssp):
    compared_df = f"{changed_provinces_path}/ssp{ssp}_predicted_changed_provinces.csv"
    compared_df = pd.read_csv(compared_df)
    compared_df = compared_df[compared_df["changed"]].reset_index(drop=True)
    return compared_df



def attach_future_env(compared_df, future_df, predictor_columns):
    compared_df = compared_df.copy()
    compared_df["point_id"] = np.arange(len(compared_df))

    # convert changed points to meters
    compared_gdf = gpd.GeoDataFrame(
        compared_df,
        geometry=gpd.points_from_xy(
            compared_df["longitude"],
            compared_df["latitude"],
        ),
        crs="EPSG:4326"
    ).to_crs("EPSG:3395")

    # convert future points to meters
    future_gdf = gpd.GeoDataFrame(
        future_df[predictor_columns],
        geometry=gpd.points_from_xy(
            future_df["longitude"],
            future_df["latitude"],
        ),
        crs="EPSG:4326"
    ).to_crs("EPSG:3395")
    
    matched = gpd.sjoin_nearest(
        compared_gdf, 
        future_gdf,
        how="left",
        distance_col="match_distance"   
    )

    # keep nearest match only
    matched = matched.sort_values(["point_id", "match_distance"]).drop_duplicates("point_id", keep="first")
    matched = matched.reset_index(drop=True)

    return matched



def compute_zscore(matched_df, predictor_columns, present_mean, present_std):
    # compute z-scores and record their column names
    z_columns = []
    for var in predictor_columns:
        z_col = f"z_{var}"
        matched_df[z_col] = (matched_df[var] - present_mean[var]) / present_std[var]
        z_columns.append(z_col)

    # convert all z-score columns into a np array
    z_values = matched_df[z_columns].to_numpy(dtype=float)

    # find the variable with the largest absolute z-score for each grid cell
    dominant_idx = np.abs(z_values).argmax(axis=1)

    # record the dominant variable and its original signed z-score
    matched_df["dominant_driver"] = [predictor_columns[i] for i in dominant_idx]
    matched_df["dominant_z"] = z_values[np.arange(len(z_values)), dominant_idx]

    return matched_df, z_columns



def process_ssp(ssp, predictor_columns, present_mean, present_std):
    compared_df = load_compared_df(ssp)
    future_df = load_future_df(ssp, predictor_columns)
    matched_df = attach_future_env(compared_df, future_df, predictor_columns)

    # breakpoint()

    result_df, z_columns = compute_zscore(matched_df, predictor_columns, present_mean, present_std)

    output_columns = ["latitude", "longitude", "baseline_provinces", "ssp_provinces"] + predictor_columns + z_columns + ["dominant_driver", "dominant_z", "match_distance"]
    result_df = result_df[output_columns]

    result_df.to_csv(f"{output_path}/driver_zscores_ssp{ssp}.csv")



def main():
    os.makedirs(output_path, exist_ok=True)

    predictor_columns_10 = get_predictor_columns("119")
    present_mean_10, present_std_10 = compute_present_day_stats(predictor_columns_10)
    for ssp in ["119", "126", "370", "460", "585"]:
        process_ssp(ssp, predictor_columns_10, present_mean_10, present_std_10)

    predictor_columns_9 = get_predictor_columns("245")
    present_mean_9, present_std_9 = compute_present_day_stats(predictor_columns_9)
    process_ssp("245", predictor_columns_9, present_mean_9, present_std_9)
    

if __name__ == "__main__":
    main()

