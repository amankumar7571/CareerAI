import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pickle
from pathlib import Path

try:
    import xgboost as xgb
except ImportError:
    xgb = None


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "synthetic_career_data.csv"
MODEL_PATH = BASE_DIR / "career_model.pkl"
FEATURES_PATH = BASE_DIR / "career_model_features.pkl"
ENCODER_PATH = BASE_DIR / "career_roles_encoder.pkl"

def train():
    if not DATA_PATH.exists():
        print("Data file not found. Run generate_data.py first.")
        return

    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    
    # Features (X) and Target (y)
    X = df.drop(columns=["Role"])
    y = df["Role"]
    
    # Store feature names to ensure inference is aligned
    feature_names = list(X.columns)
    with open(FEATURES_PATH, "wb") as f:
        pickle.dump(feature_names, f)
        
    # We must encode the target labels to numeric for XGBoost
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(le, f)

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    print("Training Logistic Regression...")
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_preds)
    
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    
    scores = {"Logistic Regression": (lr_acc, lr), "Random Forest": (rf_acc, rf)}

    accuracy_lines = [f"LR: {lr_acc:.4f}", f"RF: {rf_acc:.4f}"]
    if xgb is not None:
        print("Training XGBoost...")
        xb = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
        xb.fit(X_train, y_train)
        xb_preds = xb.predict(X_test)
        xb_acc = accuracy_score(y_test, xb_preds)
        scores["XGBoost"] = (xb_acc, xb)
        accuracy_lines.append(f"XGB: {xb_acc:.4f}")
    else:
        print("XGBoost not installed. Skipping that model.")
    
    print(f"\nAccuracy Scores:\n" + "\n".join(accuracy_lines))
    
    # Select best model
    best_model = None
    best_name = ""
    
    for name, (acc, model) in scores.items():
        if best_model is None or acc > scores[best_name][0]:
            best_model = model
            best_name = name
            
    print(f"\nSelected Best Model: {best_name} with accuracy {scores[best_name][0]:.4f}")
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)
    print("Model saved as career_model.pkl")

if __name__ == "__main__":
    train()
