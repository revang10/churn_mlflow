import pandas as pd
import psycopg2
from datetime import datetime,timedelta
from dotenv import load_dotenv
load_dotenv()
import os


# =================
# CONFIG           |
# =================


# DB YRL TO CONNECT TO SUPABASE DATABASE

DB_URL = f"postgresql://postgres.yqdyyodjoguitgokgmof:{os.getenv("DB_PASSWORD")}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
print(DB_URL)

OBS_WINDOW_DAYS = 30
CHURN_WINDOW_DAYS =30



# =================
# LOAD DATA        |
# =================

conn = psycopg2.connect(DB_URL)

customers = pd.read_sql("SELECT * FROM customers",conn)
orders = pd.read_sql("SELECT * FROM orders",conn)
tickets = pd.read_sql("SELECT * FROM support_tickets",conn)

conn.close
# Converted in date time
orders["order_date"] = pd.to_datetime(orders["order_date"])
tickets["created_date"] = pd.to_datetime(tickets["created_date"])
customers["signup_date"] = pd.to_datetime(customers["signup_date"])




# =====================
# DEFINE CUTOFF DATE   |
# =====================

max_order_date = orders["order_date"].max()
cutoff_date = max_order_date- timedelta(days=CHURN_WINDOW_DAYS)

print(f"Max order date   : {max_order_date}")
print(f"Cutoff date used : {cutoff_date}")




# ======================
# FEATURE ENGINEERING   |
# ======================

features = []

for _, customer in customers.iterrows():
    cid = customer["customer_id"]

    cust_order = orders[orders["customer_id"]==cid]
    cust_tickets = tickets[tickets["customer_id"] == cid]

    # Usable order data //// Keep only orders that happened before cutoff
    cust_orders = cust_order[cust_order["order_date"]<= cutoff_date]

    if cust_orders.empty:
        continue

    # Observation date = customer's last usable order
    observation_date = cust_orders["order_date"].max()

    print("The Observation date is  :",observation_date)



    # ==============================
    # Observation window (PAST)     |
    # ==============================

    obs_start = observation_date - timedelta(days=OBS_WINDOW_DAYS)
    print("The observation Start date is  :",obs_start)

    past_orders = cust_orders[
        (cust_orders["order_date"] >= obs_start) &
        (cust_orders["order_date"] <= observation_date)
    ]
    past_tickets = cust_tickets[
        (cust_tickets["created_date"] >= obs_start) &
        (cust_tickets["created_date"] <= observation_date)
    ]

    print("The past order data is as follows /n",past_orders)
    print("The past tickets data is as follows /n",past_tickets)



    # ==============================
    # Churn window (FUTURE)         |
    # ==============================

    future_orders = orders[
        (orders["customer_id"] == cid) &
        (orders["order_date"] > observation_date) &
        (orders["order_date"] <= observation_date + timedelta(days=CHURN_WINDOW_DAYS))
    ]

    churn = int(len(future_orders)==0)  



    # ================
    # Feature row     |
    # ================

    features.append({
        "customer_id" : cid,
        "order_las_30_days": len(past_orders),
        "avg_delivery_time": past_orders["delivery_time_minutes"].mean() if len(past_orders)>0 else 0 ,
        "late_delivery_ratio": past_orders["was_delayed"].mean() if len(past_orders) > 0 else 0,
        "avg_order_value" : past_orders["order_value"].mean()if len(past_orders) > 0 else 0,
        "support_tickets_last_30_days": len(past_tickets),
        "days_since_last_order": (observation_date - past_orders["order_date"].max()).days,
        "churn" : churn
    })



# ================
# SAVE DATASET    |
# ================

df_features = pd.DataFrame(features)
df_features.to_csv("data/processed/churn_training_data.csv", index=False)
print("✅ Feature dataset created successfully")
print(df_features["churn"].value_counts())
print(df_features.head())


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# You can confidently explain:

# "I define a cutoff date to ensure future data exists for churn labeling.
# For each customer, I compute features from a fixed observation window before 
# their last usable activity and label churn based on the absence of orders in a future window."
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

