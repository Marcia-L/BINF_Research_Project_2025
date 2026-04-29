"""
Comparing projected provinces of SSPs with the baseline to find the changed area.

Usage:
    python compare_baseline_and_ssps_provinces.py

"""

import pandas as pd


def baseline_provinces():
    baseline_province = "/data/gpfs/projects/punim2700/outputs/global_province_predictions/baseline_predicted_provinces.csv"
    baseline_province = pd.read_csv(baseline_province).head(1000)
    #for col in ["latitude", "longitude"]:
        #baseline_province[col] = ((baseline_province[col]/0.05).round() * 0.05).round(2)
    baseline_province = baseline_province.set_index(["latitude", "longitude"])
    return baseline_province


def ssp_provinces(ssp):
    ssp_province = f"/data/gpfs/projects/punim2700/outputs/global_province_predictions/ssp{ssp}_predicted_provinces.csv"
    ssp_province = pd.read_csv(ssp_province).head(1000)
    #for col in ["latitude", "longitude"]:
        #ssp_province[col] = ((ssp_province[col]/0.05).round() * 0.05).round(2)
    ssp_province = ssp_province.set_index(["latitude", "longitude"])
    return ssp_province


def compare_provinces(baseline_province, ssp_province, ssp):
    merged = ssp_province.join(baseline_province, how="inner")
    merged["changed"] = (merged["predicted_provinces"] != merged["baseline_provinces"])
    changed = merged["changed"]
    breakpoint()
    changed.to_csv(f"/data/gpfs/projects/punim2700/outputs/global_province_changes/ssp{ssp}_predicted_changed_points.csv")
    print("merged rows:", len(merged))
    print("changed rows:", len(changed))
    

def main():
    baseline_province = baseline_provinces()
    
    for ssp in ["119", "126", "245", "370", "460", "585"]: 
        ssp_province = ssp_provinces(ssp)
        compare_provinces(baseline_province, ssp_province, ssp)
        print("baseline rows:", len(baseline_province))
        print("ssp rows:", len(ssp_province))
        


if __name__ == "__main__":
    main()
