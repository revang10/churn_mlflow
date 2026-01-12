<<<<<<< HEAD
# 📊 Customer Retention Intelligence System (ML + MLOps)

This project demonstrates an **end-to-end Machine Learning + MLOps pipeline** for identifying customers at risk of disengagement using **synthetic data**, **experiment tracking**, **model registry**, and **real-time model serving**.

The goal is to showcase **production-oriented ML practices**, not just model training.

---

## 🎯 Project Goal

- Build a **realistic ML pipeline** similar to industry workflows  
- Prevent **data leakage** using time-based feature engineering  
- Track experiments and models using **MLflow**  
- Deploy a **production-approved model** as a real-time API using **FastAPI**

---

## 🧠 What This Project Solves

In real businesses:

- Customers gradually stop engaging
- Companies want **early warning signals** before losing customers

This system:

- Learns customer behavior patterns from historical activity
- Assigns a **retention risk (churn) label**
- Serves predictions via an API for downstream applications

---

## 🏗️ Tech Stack Used

- **Python**
- **PostgreSQL (Supabase)** – data storage
- **Pandas, NumPy** – data processing
- **Scikit-learn** – model training
- **MLflow** – experiment tracking & model registry
- **FastAPI** – real-time model serving
- **Uvicorn** – API server

---

## 📁 Project Structure

```text
churn-mlops/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── data/
│   │   └── generate_data.py
│   │
│   ├── features/
│   │   └── build_features.py
│   │
│   ├── models/
│   │   ├── train_model.py
│   │   └── serving/
│   │       └── app.py
│
├── mlruns/                 # MLflow tracking data
├── .env
├── requirements.txt
└── README.md


## ⚙️ Setup Instructions

### 1️⃣ Create Virtual Environment

    python -m venv venv   
    # Windows: venv\Scripts\activate

### 2️⃣ Install Dependencies

    pip install -r requirements.txt

### 3️⃣ Environment Variables

Create a .env file:

    DB_PASSWORD=your_supabase_db_password

--------------------------------------------------
```
## 🚀 How to Run the Project (Step-by-Step)

### Step 1: Generate Synthetic Data

Creates realistic customers, orders, and support tickets.

    python src/data/generate_data.py

✔ Inserts data into PostgreSQL (Supabase)

--------------------------------------------------

### Step 2: Feature Engineering + Label Creation

- Uses an observation window (past behavior)
- Uses a future window to label retention risk
- Prevents data leakage

    python src/features/build_features.py

✔ Output:
    
    data/processed/churn_training_data.csv

--------------------------------------------------

### Step 3: Train Model with MLflow

- Trains Logistic Regression
- Logs metrics, parameters, and artifacts
- Registers model in MLflow Model Registry

    python src/models/train_model.py

✔ Model registered as:

    churn_model

--------------------------------------------------

### Step 4: Promote Model to Production

Start MLflow UI:

    mlflow ui

Open:
    http://localhost:5000

Steps:
- Select latest model version
- Transition stage → Production                  

--------------------------------------------------

### Step 5: Start FastAPI Model Server

Loads the Production model directly from MLflow.

    uvicorn src.models.serving.app:app --reload

✔ API available at:

    http://127.0.0.1:8000

--------------------------------------------------

### Step 6: Test the API (Example)

    curl -X POST "http://127.0.0.1:8000/predict" \
    -H "Content-Type: application/json" \
    -d '{
      "order_last_30_days": 3,
      "avg_delivery_time": 42,
      "late_delivery_ratio": 0.3,
      "avg_order_value": 520,
      "support_tickets_last_30_days": 1,
      "days_since_last_order": 5
    }'

✔ Response:

    {
      "churn_probability": 0.27,
      "prediction": 0
    }
=======
# churn_mlflow
>>>>>>> eb18bc0c52496639c7c5386580619f13fc107ed2
