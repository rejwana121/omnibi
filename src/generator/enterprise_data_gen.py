"""
Enterprise Synthetic Data Generator for OmniBI.
Generates realistic multi-dimensional retail transactions, customer churn signals,
and customer support records, then populates the DuckDB data warehouse.
"""

import random
from datetime import datetime, timedelta
import uuid
from faker import Faker
import pandas as pd
from src.database.connection import DuckDBManager

fake = Faker()
Faker.seed(42)
random.seed(42)

REGIONS = {
    "North America": ["USA", "Canada"],
    "Europe": ["Germany", "UK", "France", "Spain", "Netherlands"],
    "Asia-Pacific": ["Japan", "Singapore", "Australia", "India"],
    "Latin America": ["Brazil", "Mexico"]
}

CATEGORIES = {
    "Electronics": ["Laptops", "Smartphones", "Audio", "Monitors", "Accessories"],
    "Apparel": ["Men's Wear", "Women's Wear", "Activewear", "Footwear"],
    "Home & Office": ["Ergonomic Chairs", "Standing Desks", "Lighting", "Coffee Machines"],
    "Cloud Services": ["Compute Instances", "Storage Tier", "Security Audit", "API Access"],
    "Health & Fitness": ["Smart Trackers", "Supplements", "Yoga Gear", "Gym Equipment"]
}

SEGMENTS = ["Enterprise", "Mid-Market", "SMB", "Consumer"]
LOYALTY_TIERS = ["Platinum", "Gold", "Silver", "Bronze"]
CHANNELS = ["Web", "Mobile App", "B2B Portal", "Partner"]
PAYMENTS = ["Credit Card", "Wire Transfer", "PayPal", "Stripe"]
ORDER_STATUSES = ["Delivered", "Shipped", "Processing", "Cancelled", "Returned"]
ISSUE_CATEGORIES = ["Billing", "Shipping Delay", "Defective Item", "Return Request", "Account Access"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]


def generate_customers(n: int = 500) -> pd.DataFrame:
    customers = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2026, 6, 1)

    for i in range(1, n + 1):
        region = random.choice(list(REGIONS.keys()))
        country = random.choice(REGIONS[region])
        signup = fake.date_between(start_date=start_date, end_date=end_date)
        segment = random.choices(SEGMENTS, weights=[0.15, 0.25, 0.35, 0.25])[0]
        
        # Churn risk score higher for lower satisfaction/segment
        churn_risk = round(random.betavariate(2, 5), 2)
        loyalty = random.choices(LOYALTY_TIERS, weights=[0.1, 0.25, 0.35, 0.3])[0]

        customers.append({
            "customer_id": f"CUST_{i:04d}",
            "customer_name": fake.company() if segment in ["Enterprise", "Mid-Market"] else fake.name(),
            "email": fake.company_email() if segment in ["Enterprise", "Mid-Market"] else fake.email(),
            "segment": segment,
            "region": region,
            "country": country,
            "signup_date": signup,
            "churn_risk_score": churn_risk,
            "loyalty_tier": loyalty
        })
    return pd.DataFrame(customers)


def generate_products(n: int = 80) -> pd.DataFrame:
    products = []
    pid = 1
    for cat, subcats in CATEGORIES.items():
        for subcat in subcats:
            for _ in range(2):
                cost = round(random.uniform(15.0, 450.0), 2)
                margin = random.uniform(1.25, 2.1)
                price = round(cost * margin, 2)
                products.append({
                    "product_id": f"PROD_{pid:03d}",
                    "product_name": f"{subcat} {fake.word().capitalize()} Model-{random.randint(10, 99)}",
                    "category": cat,
                    "sub_category": subcat,
                    "unit_cost": cost,
                    "unit_price": price,
                    "stock_quantity": random.randint(50, 2000)
                })
                pid += 1
    return pd.DataFrame(products)


def generate_orders_and_items(
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    n_orders: int = 5000
) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders = []
    order_items = []
    cust_ids = customers_df["customer_id"].tolist()
    prod_lookup = products_df.set_index("product_id").to_dict("index")
    prod_ids = list(prod_lookup.keys())

    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 10, 15)
    item_counter = 1

    for o in range(1, n_orders + 1):
        order_id = f"ORD_{o:05d}"
        cust_id = random.choice(cust_ids)
        timestamp = fake.date_time_between(start_date=start_date, end_date=end_date)
        channel = random.choices(CHANNELS, weights=[0.45, 0.35, 0.15, 0.05])[0]
        payment = random.choice(PAYMENTS)
        status = random.choices(ORDER_STATUSES, weights=[0.82, 0.06, 0.04, 0.04, 0.04])[0]

        # Order line items (1 to 4 items per order)
        num_items = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
        selected_prods = random.sample(prod_ids, num_items)
        
        order_subtotal = 0.0
        for p_id in selected_prods:
            qty = random.randint(1, 4)
            unit_price = prod_lookup[p_id]["unit_price"]
            unit_cost = prod_lookup[p_id]["unit_cost"]
            line_total = round(qty * unit_price, 2)
            line_profit = round(line_total - (qty * unit_cost), 2)
            order_subtotal += line_total

            order_items.append({
                "item_id": f"ITEM_{item_counter:06d}",
                "order_id": order_id,
                "product_id": p_id,
                "quantity": qty,
                "unit_price": unit_price,
                "unit_cost": unit_cost,
                "line_total": line_total,
                "line_profit": line_profit
            })
            item_counter += 1

        discount = round(order_subtotal * random.choice([0.0, 0.05, 0.1, 0.15]), 2)
        shipping = round(random.choice([0.0, 9.99, 14.99, 24.99]), 2)
        total_amount = round(order_subtotal - discount + shipping, 2)

        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "order_timestamp": timestamp,
            "channel": channel,
            "payment_method": payment,
            "total_amount": total_amount,
            "discount_amount": discount,
            "shipping_cost": shipping,
            "order_status": status
        })

    return pd.DataFrame(orders), pd.DataFrame(order_items)


def generate_support_tickets(customers_df: pd.DataFrame, n_tickets: int = 1200) -> pd.DataFrame:
    tickets = []
    cust_ids = customers_df["customer_id"].tolist()
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 10, 15)

    for t in range(1, n_tickets + 1):
        created = fake.date_time_between(start_date=start_date, end_date=end_date)
        priority = random.choices(PRIORITIES, weights=[0.1, 0.3, 0.4, 0.2])[0]
        
        # High priority resolves faster or has lower satisfaction if delayed
        resolution_hrs = round(random.expovariate(1.0 / 18.0) + 1.0, 1)
        sat = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.15, 0.25, 0.3, 0.2])[0]

        tickets.append({
            "ticket_id": f"TCK_{t:04d}",
            "customer_id": random.choice(cust_ids),
            "created_at": created,
            "issue_category": random.choice(ISSUE_CATEGORIES),
            "priority": priority,
            "resolution_time_hrs": resolution_hrs,
            "satisfaction_score": sat
        })
    return pd.DataFrame(tickets)


def seed_database():
    """Generates and writes all synthetic tables into DuckDB."""
    print("Connecting to DuckDB...")
    db = DuckDBManager(read_only=False)
    
    print("Generating Customers...")
    df_customers = generate_customers(500)
    
    print("Generating Products...")
    df_products = generate_products(80)
    
    print("Generating Orders and Order Line Items...")
    df_orders, df_items = generate_orders_and_items(df_customers, df_products, 5000)
    
    print("Generating Support Tickets...")
    df_tickets = generate_support_tickets(df_customers, 1200)

    print("Registering and writing tables into DuckDB...")
    # Clear any previous data and insert cleanly
    db.conn.register("tmp_customers", df_customers)
    db.conn.execute("INSERT OR REPLACE INTO dim_customers SELECT * FROM tmp_customers")
    
    db.conn.register("tmp_products", df_products)
    db.conn.execute("INSERT OR REPLACE INTO dim_products SELECT * FROM tmp_products")
    
    db.conn.register("tmp_orders", df_orders)
    db.conn.execute("INSERT OR REPLACE INTO fact_orders SELECT * FROM tmp_orders")
    
    db.conn.register("tmp_items", df_items)
    db.conn.execute("INSERT OR REPLACE INTO fact_order_items SELECT * FROM tmp_items")
    
    db.conn.register("tmp_tickets", df_tickets)
    db.conn.execute("INSERT OR REPLACE INTO fact_support_tickets SELECT * FROM tmp_tickets")

    print("\n--- Verification Summary ---")
    for tbl in ["dim_customers", "dim_products", "fact_orders", "fact_order_items", "fact_support_tickets"]:
        cnt = db.conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"Table '{tbl}': {cnt:,} records.")

    db.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
