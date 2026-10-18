-- OmniBI Enterprise Analytics Star Schema (DuckDB)

-- Dimension: Customers
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    email VARCHAR,
    segment VARCHAR NOT NULL, -- Enterprise, Mid-Market, SMB, Consumer
    region VARCHAR NOT NULL,  -- North America, Europe, Asia-Pacific, Latin America
    country VARCHAR NOT NULL,
    signup_date DATE NOT NULL,
    churn_risk_score DOUBLE,  -- 0.00 to 1.00
    loyalty_tier VARCHAR      -- Platinum, Gold, Silver, Bronze
);

-- Dimension: Products
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    sub_category VARCHAR,
    unit_cost DOUBLE NOT NULL,
    unit_price DOUBLE NOT NULL,
    stock_quantity INTEGER NOT NULL
);

-- Fact: Orders (Transaction Header)
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR REFERENCES dim_customers(customer_id),
    order_timestamp TIMESTAMP NOT NULL,
    channel VARCHAR NOT NULL,        -- Web, Mobile App, B2B Portal, Partner
    payment_method VARCHAR NOT NULL, -- Credit Card, Wire Transfer, PayPal, Stripe
    total_amount DOUBLE NOT NULL,
    discount_amount DOUBLE DEFAULT 0.0,
    shipping_cost DOUBLE DEFAULT 0.0,
    order_status VARCHAR NOT NULL    -- Delivered, Shipped, Processing, Cancelled, Returned
);

-- Fact: Order Items (Transaction Line Items)
CREATE TABLE IF NOT EXISTS fact_order_items (
    item_id VARCHAR PRIMARY KEY,
    order_id VARCHAR REFERENCES fact_orders(order_id),
    product_id VARCHAR REFERENCES dim_products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DOUBLE NOT NULL,
    unit_cost DOUBLE NOT NULL,
    line_total DOUBLE NOT NULL,
    line_profit DOUBLE NOT NULL
);

-- Fact: Customer Support & Experience
CREATE TABLE IF NOT EXISTS fact_support_tickets (
    ticket_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR REFERENCES dim_customers(customer_id),
    created_at TIMESTAMP NOT NULL,
    issue_category VARCHAR NOT NULL,  -- Billing, Shipping Delay, Defective Item, Return Request
    priority VARCHAR NOT NULL,        -- Critical, High, Medium, Low
    resolution_time_hrs DOUBLE,
    satisfaction_score INTEGER        -- 1 (Poor) to 5 (Excellent)
);

-- Analytical Indexes
CREATE INDEX IF NOT EXISTS idx_orders_cust ON fact_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON fact_orders(order_timestamp);
CREATE INDEX IF NOT EXISTS idx_items_order ON fact_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_items_prod ON fact_order_items(product_id);
