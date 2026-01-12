import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix
)

import mlflow
import mlflow.sklearn

# =========================
# CONFIG
# =========================

DATA_PATH = "data/processed/churn_training_data.csv"
EXPERIMENT_NAME = "customer_churn_prediction"
TEST_SIZE = 0.2
RANDOM_STATE = 42

# =========================
# MLflow Setup
# =========================

mlflow.set_experiment(EXPERIMENT_NAME)

# =========================
# LOAD DATA
# =========================

df = pd.read_csv(DATA_PATH)

X = df.drop(columns=["customer_id", "churn"])
y = df["churn"]

print("Churn distribution:")
print(y.value_counts(normalize=True))

# =========================
# TRAIN / TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    stratify=y,
    random_state=RANDOM_STATE
)

# =========================
# TRAIN + TRACK
# =========================

with mlflow.start_run():

    # ---- Parameters ----
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("class_weight", "balanced")
    mlflow.log_param("test_size", TEST_SIZE)

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE
    )

    model.fit(X_train, y_train)

    # ---- Evaluation ----
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    roc_auc = roc_auc_score(y_test, y_prob)
    report = classification_report(y_test, y_pred, output_dict=True)

    mlflow.log_metric("roc_auc", roc_auc)
    mlflow.log_metric("precision_churn", report["1"]["precision"])
    mlflow.log_metric("recall_churn", report["1"]["recall"])
    mlflow.log_metric("f1_churn", report["1"]["f1-score"])

    # ---- Log model ----
    mlflow.sklearn.log_model(
    sk_model=model,
    artifact_path="model",
    registered_model_name="churn_model"
    )


    # ---- Logs ----
    print("\nROC AUC:", roc_auc)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

print("\n✅ Model trained and logged to MLflow")
