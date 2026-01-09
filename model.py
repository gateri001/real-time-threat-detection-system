import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

FEATURES = ["bytes","pkts"]

def train_model(normal_df, save_path="isoforest.joblib"):
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    model.fit(normal_df[FEATURES])
    joblib.dump(model, save_path)
    return model

def load_model(path="isoforest.joblib"):
    import joblib
    return joblib.load(path)

def score_event(model, event):
    # Build a DataFrame with correct feature names
    df = pd.DataFrame([{
        "bytes": event.get("bytes", 0),
        "pkts": event.get("pkts", 0)
    }], columns=model.feature_names_in_)

    # Get normality score
    score = model.decision_function(df)[0]

    # Invert (higher = more anomalous)
    anomaly_score = -score  
    return float(anomaly_score)

