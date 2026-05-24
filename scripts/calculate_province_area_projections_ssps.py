"""
Calculate province area projections using sklearn RandomForestClassifier.
This script runs the model for 5 ssp scenarios, except for ssp245.

Usage:
    python calculate_province_area_projections_ssps.py

"""

import pandas as pd
import xarray as xr
from sklearn.ensemble import RandomForestClassifier


def train_clf(X, y):
    """
    Train RandomForest Classifier.

    Params:
        X: sample baseline (~1454 samples)
        y: provinces

    Returns:
        clf: fitted RandomForest classifier
    """
    clf = RandomForestClassifier()
    clf.fit(X, y)
    return clf


def fit_random_forest(clf, X):
    """
    Fits RF Classifier to global data layer.

    Params:
        clf: RandomForest classifier fitted with sample data
        X: global baseline data_layer (16kk coordinate points)

    Returns:
        y_hat: predictions for global data layer
    """
    y_hat = clf.predict(X)
    return y_hat


def predict_ssp(ssp):
    # Loading sample baseline data
    # Make sure these paths work
    sample_baseline = "/data/gpfs/projects/punim2700/data/share/sample_scenarios/baseline_samples.csv"
    sample_metadata = "/data/gpfs/projects/punim2700/data/share/sample_metadata.csv"

    columns_to_remove = ['DiffuseAttenuationCoefficientPAR', 'MixedLayerDepth', 'SeaWaterSpeed', 'PhotosyntheticallyAvailableRadiation', 'Terrain',
                         'AirTemperature', 'SeaIceThickness', 'TotalCloudFraction', 'TotalPhytoplankton']
    
    sample_baseline = pd.read_csv(sample_baseline, index_col=0).drop(columns_to_remove, axis=1)
    sample_metadata = pd.read_csv(sample_metadata, index_col=0)

    # Preparing RF model
    X_train = sample_baseline
    y_train = sample_metadata["picoplankton_province"]
    
    # breakpoint()
    

    # Set lat/lon as spatial index for alignment with global layer 
    coords = sample_metadata.loc[X_train.index, ["latitude", "longitude"]]
    X_train.index = pd.MultiIndex.from_frame(coords)
    X_train.index = X_train.index.set_names(["latitude", "longitude"])
    
    clf = train_clf(X_train, y_train)

    # Loading global data
    global_scenario = f"/data/gpfs/projects/punim2700/data/share/global_scenarios/ssp{ssp}_env_data.nc"
    global_scenario = xr.open_dataset(global_scenario)
    X = global_scenario.to_dataframe().dropna(how="any").reset_index()


    # breakpoint()

    # Keep only predictor variables used in training
    X = X[X_train.columns]
    
    
    # Fit the model
    y_hat = fit_random_forest(clf, X)
    y_hat = pd.Series(y_hat, index=X.index, name="predicted_provinces")

    y_hat.to_csv(f"/data/gpfs/projects/punim2700/outputs/global_province_predictions/ssp{ssp}_predicted_provinces.csv")


def main():
    # ssp245 is handled separately as it doesn't include column ["Nitrate"]
    for ssp in ["119", "126", "370", "460", "585"]: 
        predict_ssp(ssp)


if __name__ == "__main__":
    main()
