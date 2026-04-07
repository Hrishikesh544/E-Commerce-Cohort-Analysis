import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Seed for reproducibility
np.random.seed(42)

# 1. SCALED UP: Creating 100 Products data
productid = np.arange(101, 201)
categories = ['Clothing', "Home", "Electronics", "Books"]
product_df = pd.DataFrame({
    'product_id' : productid,
    'category' : np.random.choice(categories, len(productid)),
    'price' : np.random.randint(500, 5000, len(productid))
})

# 2. SCALED UP: Creating 2000 users 
userid = np.arange(1, 2001)
cities = ['Pune','Bangalore','Mumbai','Delhi','Hyderabad']
user_df = pd.DataFrame({
    'user_id' : userid,
    'city' : np.random.choice(cities, len(userid)),
    # Random dates over a year
    'signup_date' : [datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(len(userid))] 
})

# 3. SCALED UP: 15,000 Orders spread across a full 365 days 
num_orders = 15000
order_df = pd.DataFrame({
    'order_id': np.arange(1001, 1001 + num_orders),
    'user_id': np.random.choice(userid, num_orders),
    'product_id': np.random.choice(productid, num_orders),
    'order_date': [datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(num_orders)]
})
print("Massive Tables Created Successfully!")

# Create a db file connection with local db
conn = sqlite3.connect('Project.db')

user_df.to_sql('users', conn, index=False, if_exists='replace')
product_df.to_sql('products', conn, index=False, if_exists='replace')
order_df.to_sql('orders', conn, index=False, if_exists='replace')

###########################################################################################
# The SQL Query (The "Extraction" Phase)
query = """
SELECT 
    o.order_id,
    o.order_date,
    u.user_id,
    u.city,
    p.category,
    p.price
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN products p ON o.product_id = p.product_id
"""
# Execute the SQL query
master_df = pd.read_sql_query(query, conn)
print("15,000+ rows successfully joined and extracted from SQL!")

###############################################

# 1. Create the 'order_month' column 
master_df['order_month'] = pd.to_datetime(master_df['order_date']).dt.to_period('M')

# 2. Create the 'cohort_month' column
master_df['cohort_month'] = master_df.groupby('user_id')['order_month'].transform('min')

# 3. Calculate the 'cohort_index' 
order_year = master_df['order_month'].dt.year
order_month = master_df['order_month'].dt.month

cohort_year = master_df['cohort_month'].dt.year
cohort_month = master_df['cohort_month'].dt.month

year_diff = order_year - cohort_year
month_diff = order_month - cohort_month
master_df['cohort_index'] = year_diff * 12 + month_diff + 1

##################################################################################################################

# 1. Count UNIQUE users in each cohort bucket
cohort_data = master_df.groupby(['cohort_month', 'cohort_index'])['user_id'].nunique().reset_index()

# 2. Pivot the data into a grid
cohort_counts = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='user_id')

# 3. Calculate Retention Rates (Percentages)
cohort_sizes = cohort_counts.iloc[:, 0]
retention = cohort_counts.divide(cohort_sizes, axis=0) * 100

# --- THE CRAFTSMAN FIX: Force the index to be clean strings before plotting ---
retention.index = retention.index.astype(str)

# 4. Plot the Heatmap
plt.figure(figsize=(14, 8)) 
plt.title('Customer Retention by Monthly Cohorts (%)', fontsize=16, fontweight='bold')

sns.heatmap(data=retention, 
            annot=True, 
            fmt='.1f',  
            cmap='Blues', 
            vmin=0, vmax=100) 

# --- THE MAGIC FIX: Force the Y-axis labels to stay horizontal so they don't overlap ---
plt.yticks(rotation=0) 

plt.ylabel('Cohort Month (First Purchase)')
plt.xlabel('Months Since First Purchase (Cohort Index)')
plt.tight_layout() # Ensures nothing gets cut off
plt.show()