import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import joblib, os

def toy_data(n=1000, nfeat=10):
    X = np.random.randn(n, nfeat)
    y = (X[:,0]*0.5 + X[:,1]*0.3 + np.sin(X[:,2]))*0.01 + 0.005*np.random.randn(n)
    return X, y

def train():
    X, y = toy_data()
    model = GradientBoostingRegressor(n_estimators=200, max_depth=4)
    model.fit(X, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/lightgbm_model.joblib")
    print("Saved models/lightgbm_model.joblib")

if __name__ == "__main__":
    train()
