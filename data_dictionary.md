# Data Dictionary: E-Commerce Database

This document outlines the schema for the synthetic E-Commerce database generated and analyzed in this repository.

### **Table: `users`**
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `user_id` | INT | Unique identifier for the customer (Primary Key). |
| `city` | VARCHAR | Customer's registered city (Pune, Bangalore, etc.). |
| `signup_date` | DATETIME | The exact date the user created their account. |

### **Table: `products`**
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `product_id` | INT | Unique identifier for the item (Primary Key). |
| `category` | VARCHAR | The department (Clothing, Home, Electronics, Books). |
| `price` | INT | Cost of the item in INR. |

### **Table: `orders`**
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `order_id` | INT | Unique identifier for the transaction (Primary Key). |
| `user_id` | INT | The customer making the purchase (Foreign Key). |
| `product_id` | INT | The item purchased (Foreign Key). |
| `order_date` | DATETIME | The timestamp of the transaction. |

### **Engineered Features (Pandas Pipeline)**
| Feature Name | Description |
| :--- | :--- |
| `order_month` | The exact Year-Month period of a transaction. |
| `cohort_month` | The minimum `order_month` for a specific user (Their first purchase). |
| `cohort_index` | The integer difference in months between the `order_month` and `cohort_month`. |