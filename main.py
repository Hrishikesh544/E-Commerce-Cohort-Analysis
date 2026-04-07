import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

#seed for reproducibility
np.random.seed(42)

#creating Products data
productid = np.arange(101,111)
categories = ['Clothing', "Home", "Electronics", "Books"]
product_df = pd.DataFrame({
  'product_id' : productid,
  'category' : np.random.choice(categories,len(productid)),
  'price' : np.random.randint(500,5000,len(productid))
})

#creating users data
userid = np.arange(1,101)
cities = ['Pune','Bangalore','Mumbai','Delhi','Hyderabad']
user_df = pd.DataFrame({
  'user_id' : userid,
  'city' : np.random.choice(cities,len(userid)),
  'signup_date' : pd.date_range(start = '2025-01-01',periods = len(userid),freq = 'D') 
})


#Orders table messy data
num_orders = 500
order_df = pd.DataFrame({
    'order_id': np.arange(1001, 1001 + num_orders),
    'user_id': np.random.choice(userid, num_orders),
    'product_id': np.random.choice(productid, num_orders),
    'order_date': [datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 90)) for _ in range(num_orders)]
})
print("Tables Created Successfully!")
# print(product_df.head(3))

#create a db file connection with local db
conn = sqlite3.connect('Project.db')

user_df.to_sql('users' , conn , index=False, if_exists = 'replace')
product_df.to_sql('products', conn , index=False, if_exists = 'replace')
order_df.to_sql('orders' , conn , index = False , if_exists = 'replace')
###########################################################################################
# The SQL Query (The "Extraction" Phase)
# We want a unified view: Who bought what, where do they live, and how much did they spend?
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
# Execute the SQL query and load the result straight into a new Pandas DataFrame!
master_df = pd.read_sql_query(query, conn)

print("Data successfully joined and extracted from SQL!")
print(master_df.head())

###############################################
# 1. Create the 'order_month' column by converting the exact date to a Year-Month period
master_df['order_month'] = pd.to_datetime(master_df['order_date']).dt.to_period('M')

# 2. Create the 'cohort_month' column. 
# We group by user, find their earliest ('min') order month, and assign it back to every row for that user.
master_df['cohort_month'] = master_df.groupby('user_id')['order_month'].transform('min')

# 3. Calculate the 'cohort_index' (How many months it has been since their first purchase)
# First, extract the integer year and month from both columns
order_year = master_df['order_month'].dt.year
order_month = master_df['order_month'].dt.month

cohort_year = master_df['cohort_month'].dt.year
cohort_month = master_df['cohort_month'].dt.month

# The math: (Difference in years * 12) + Difference in months + 1 (so the first month is Month 1, not Month 0)
year_diff = order_year - cohort_year
month_diff = order_month - cohort_month
master_df['cohort_index'] = year_diff * 12 + month_diff + 1

print("Cohort Metrics Engineered Successfully!")
print(master_df[['user_id', 'order_month', 'cohort_month', 'cohort_index']].head(10))
##################################################################################################################

# 1. Count the number of UNIQUE users in each cohort bucket
# We group by the first purchase month and the month index, then count unique user IDs.
cohort_data = master_df.groupby(['cohort_month', 'cohort_index'])['user_id'].nunique().reset_index()

# 2. Pivot the data into a grid (Matrix)
# Rows = Cohort Month, Columns = Cohort Index (Month 1, Month 2, etc.), Values = Number of Users
cohort_counts = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='user_id')

# 3. Calculate Retention Rates (Percentages)
# We take the count of users in Month 1 (the first column) and divide every other column by that number.
# This tells us what percentage of the original group came back.
cohort_sizes = cohort_counts.iloc[:, 0]
retention = cohort_counts.divide(cohort_sizes, axis=0) * 100

# 4. Plot the Heatmap (The Matplotlib/Seaborn Magic)
plt.figure(figsize=(10, 6)) # Set the size of the canvas
plt.title('PuneKart Customer Retention by Monthly Cohorts (%)', fontsize=14)

# We use Seaborn to draw the heatmap, passing in our retention DataFrame
sns.heatmap(data=retention, 
            annot=True, # Shows the actual numbers inside the boxes
            fmt='.1f',  # Formats the numbers to 1 decimal place
            cmap='Blues', # Uses a blue color scale
            vmin=0, vmax=100) # Sets the scale from 0% to 100%

plt.ylabel('Cohort Month (First Purchase)')
plt.xlabel('Months Since First Purchase (Cohort Index)')
plt.show() # Display the chart!
