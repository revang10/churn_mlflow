import random
import uuid
from datetime import datetime,timedelta

import numpy as np
import pandas as pd
import psycopg2
from faker import Faker

from dotenv import load_dotenv
import os

load_dotenv()

fake = Faker()

#Define the postgres db link
DB_URL = f"postgresql://postgres.yqdyyodjoguitgokgmof:{os.getenv("DB_PASSWORD")}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

print("Password loaded:", bool(os.getenv("DB_PASSWORD")))

#Connect Postgres db using supabase
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

NUM_CUSTOMERS = 500
MAX_ORDERS_PER_CUSTOMERS = 15
MAX_TICKET_PER_CUSTOMER = 3
RETURNING_PROBABILITY = 0.6
    

cities =["Mumbai","Pune","Banglore","Delhi"]
issue_type = ["Late Delivery","Wrong Item","Payment Issue"]
devices = ["Android","Ios","Web"]

customers=[]
orders=[]
tickets=[]

today = datetime.today()

# -------------------------------
# Generate customers
# -------------------------------

for _ in range(NUM_CUSTOMERS):
    customer_id = str(uuid.uuid4())
    signup_date = today - timedelta(days=random.randint(30,400))
    customers.append((
        customer_id,
        signup_date.date(),
        random.choice(cities),
        random.choice(devices)
    ))
   
# -------------------------------
# Generate orders + tickets (FIXED)
# -------------------------------
for customer in customers:
    customer_id, signup_date, _, _ = customer

    is_returning = random.random() < RETURNING_PROBABILITY

    last_order_date = signup_date + timedelta(
        days=random.randint(10, min(90, (today.date() - signup_date).days))       
    )

    num_orders = random.randint(1, MAX_ORDERS_PER_CUSTOMERS)

    # -----------------------
    # Historical orders
    # -----------------------
    for _ in range(num_orders):
        order_date = signup_date + timedelta(
            days=random.randint(1, (last_order_date - signup_date).days)
        )

        delivery_time = np.random.normal(35, 10)
        delayed = delivery_time > 45

        orders.append((
            str(uuid.uuid4()),
            customer_id,
            order_date,
            round(random.uniform(200, 800), 2),
            round(max(10, delivery_time), 2),
            delayed
        ))

    # -----------------------
    # FUTURE order → churn = 0
    # -----------------------
    if is_returning:
        future_order_date = last_order_date + timedelta(
            days=random.randint(5, 25)
        )

        if future_order_date <= today.date():
            delivery_time = np.random.normal(30, 8)
            delayed = delivery_time > 45

            orders.append((
                str(uuid.uuid4()),
                customer_id,
                future_order_date,
                round(random.uniform(250, 900), 2),
                round(max(10, delivery_time), 2),
                delayed
            ))
                 
    # -----------------------
    # Support tickets
    # -----------------------
    if random.random() < 0.3:
        ticket_date = signup_date + timedelta(
            days=random.randint(1, (last_order_date - signup_date).days)
        )

        tickets.append((
            str(uuid.uuid4()),
            customer_id,
            random.choice(issue_type),
            ticket_date
        ))


# -----------------------
# INSERT DATA INTO POSTGRES
# -----------------------

# here customer is tuple that store like this (101,21-10-2023,'mumbai','Apple')
cursor.executemany(
    "INSERT INTO customers VALUES (%s,%s,%s,%s)",
    customers
)

cursor.executemany(
    "INSERT INTO orders VALUES (%s,%s,%s,%s,%s,%s)",
    orders
)

cursor.executemany(
    "INSERT INTO support_tickets VALUES (%s, %s, %s, %s)",
    tickets
)

conn.commit()
cursor.close()
conn.close()
# Step	Meaning
# commit() --> Save everything
# cursor.close() --> Stop sending SQL
# conn.close() --> Disconnect from database
# If you close the connection before committing → ❌ data is lost.


print("✅ Synthetic data successfully inserted into Postgres")