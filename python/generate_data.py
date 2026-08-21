from pathlib import Path

from faker import Faker
import numpy as np
import pandas as pd

# ============================================================
# 1. SETUP
# ============================================================

fake = Faker("en_IN")

# Make results reproducible.
# Every time you run the program, you will get the same dataset.
np.random.seed(42)
Faker.seed(42)


# ============================================================
# 2. PROJECT / DATA FOLDER
# ============================================================

# Current file:
# Real-Time-Ecommerce-Profit/python/generate_data.py
#
# We go one level up from "python" to the project folder,
# then enter the "data" folder.

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Create data folder if it doesn't exist.
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. NUMBER OF RECORDS
# ============================================================

NUM_SUPPLIERS = 10
NUM_PRODUCTS = 50
NUM_CUSTOMERS = 100
NUM_ORDERS = 1000


# ============================================================
# 4. COMMON VALUES
# ============================================================

categories = [
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Beauty",
    "Books"
]

product_names = {
    "Electronics": [
        "Laptop",
        "Smartphone",
        "Headphones",
        "Smart Watch",
        "Bluetooth Speaker",
        "Keyboard",
        "Mouse",
        "Tablet",
        "Power Bank",
        "Monitor"
    ],
    "Fashion": [
        "T-Shirt",
        "Jeans",
        "Saree",
        "Kurta",
        "Shoes",
        "Jacket",
        "Handbag",
        "Dress",
        "Wallet",
        "Sunglasses"
    ],
    "Home & Kitchen": [
        "Mixer Grinder",
        "Cooker",
        "Bedsheet",
        "Water Bottle",
        "Coffee Maker",
        "Lamp",
        "Chair",
        "Table",
        "Storage Box",
        "Air Fryer"
    ],
    "Beauty": [
        "Face Wash",
        "Shampoo",
        "Perfume",
        "Moisturizer",
        "Lipstick",
        "Face Cream",
        "Sunscreen",
        "Hair Oil",
        "Body Lotion",
        "Makeup Kit"
    ],
    "Books": [
        "Python Programming",
        "Data Science",
        "Machine Learning",
        "Atomic Habits",
        "SQL Guide",
        "AI Fundamentals",
        "Business Analytics",
        "Statistics",
        "Deep Learning",
        "DSA Guide"
    ]
}

cities_states = [
    ("Bengaluru", "Karnataka"),
    ("Mysuru", "Karnataka"),
    ("Chennai", "Tamil Nadu"),
    ("Hyderabad", "Telangana"),
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Kolkata", "West Bengal"),
    ("Ahmedabad", "Gujarat"),
    ("Kochi", "Kerala")
]

warehouses = [
    "Bengaluru Warehouse",
    "Mumbai Warehouse",
    "Delhi Warehouse",
    "Hyderabad Warehouse",
    "Chennai Warehouse"
]

payment_methods = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Cash on Delivery"
]

return_reasons = [
    "Damaged",
    "Wrong Size",
    "Wrong Product",
    "Quality Issue",
    "Changed Mind",
    "Late Delivery"
]


# ============================================================
# 5. GENERATE SUPPLIERS
# ============================================================

print("Generating suppliers...")

suppliers = []

for i in range(1, NUM_SUPPLIERS + 1):

    supplier = {
        "supplier_id": f"S{i:03d}",
        "supplier_name": fake.company(),
        "lead_time_days": np.random.randint(2, 11),
        "supplier_rating": round(
            np.random.uniform(3.0, 5.0), 1
        )
    }

    suppliers.append(supplier)


suppliers_df = pd.DataFrame(suppliers)


# ============================================================
# 6. GENERATE PRODUCTS
# ============================================================

print("Generating products...")

products = []

for i in range(1, NUM_PRODUCTS + 1):

    category = np.random.choice(categories)

    product_name = np.random.choice(
        product_names[category]
    )

    # Add a model/version number to avoid repetitive names.
    product_name = f"{product_name} {np.random.randint(100, 999)}"

    # Cost price
    cost_price = round(
        np.random.uniform(200, 50000),
        2
    )

    # Selling price is generally higher than cost.
    markup = np.random.uniform(1.15, 1.60)

    selling_price = round(
        cost_price * markup,
        2
    )

    product = {
        "product_id": f"P{i:03d}",
        "product_name": product_name,
        "category": category,
        "cost_price": cost_price,
        "selling_price": selling_price,
        "supplier_id": np.random.choice(
            suppliers_df["supplier_id"]
        )
    }

    products.append(product)


products_df = pd.DataFrame(products)


# ============================================================
# 7. GENERATE CUSTOMERS
# ============================================================

print("Generating customers...")

customers = []

customer_segments = [
    "New",
    "Regular",
    "Premium"
]

for i in range(1, NUM_CUSTOMERS + 1):

    city, state = cities_states[
        np.random.randint(0, len(cities_states))
    ]

    customer = {
        "customer_id": f"C{i:04d}",
        "customer_name": fake.name(),
        "city": city,
        "state": state,
        "customer_segment": np.random.choice(
            customer_segments,
            p=[0.30, 0.55, 0.15]
        ),
        "signup_date": fake.date_between(
            start_date="-2y",
            end_date="-30d"
        )
    }

    customers.append(customer)


customers_df = pd.DataFrame(customers)


# ============================================================
# 8. GENERATE ORDERS
# ============================================================

print("Generating orders...")

orders = []

for i in range(1, NUM_ORDERS + 1):

    # Select customer
    customer_id = np.random.choice(
        customers_df["customer_id"]
    )

    # Select product
    product_id = np.random.choice(
        products_df["product_id"]
    )

    # Find product information
    product = products_df[
        products_df["product_id"] == product_id
    ].iloc[0]

    quantity = np.random.randint(1, 6)

    discount_percent = np.random.choice(
        [0, 5, 10, 15, 20, 25],
        p=[0.20, 0.20, 0.25, 0.20, 0.10, 0.05]
    )

    # Gross sales
    gross_amount = (
        product["selling_price"] * quantity
    )

    # Discount
    discount_amount = (
        gross_amount * discount_percent / 100
    )

    # Amount customer actually pays
    net_amount = (
        gross_amount - discount_amount
    )

    # Product cost
    product_cost = (
        product["cost_price"] * quantity
    )

    # Shipping cost
    shipping_cost = round(
        np.random.uniform(50, 500),
        2
    )

    # Payment processing fee
    payment_fee = round(
        net_amount * np.random.uniform(0.01, 0.03),
        2
    )

    # Profit
    profit = (
        net_amount
        - product_cost
        - shipping_cost
        - payment_fee
    )

    order_status = np.random.choice(
        [
            "Completed",
            "Cancelled",
            "Pending"
        ],
        p=[0.88, 0.07, 0.05]
    )

    order = {
        "order_id": f"O{i:05d}",

        "order_datetime": fake.date_time_between(
            start_date="-90d",
            end_date="now"
        ),

        "customer_id": customer_id,

        "product_id": product_id,

        "quantity": quantity,

        "selling_price": round(
            product["selling_price"],
            2
        ),

        "discount_percent": discount_percent,

        "gross_amount": round(
            gross_amount,
            2
        ),

        "discount_amount": round(
            discount_amount,
            2
        ),

        "net_amount": round(
            net_amount,
            2
        ),

        "product_cost": round(
            product_cost,
            2
        ),

        "shipping_cost": shipping_cost,

        "payment_fee": payment_fee,

        "profit": round(
            profit,
            2
        ),

        "order_status": order_status
    }

    orders.append(order)


orders_df = pd.DataFrame(orders)


# ============================================================
# 9. GENERATE PAYMENTS
# ============================================================

print("Generating payments...")

payments = []

for _, order in orders_df.iterrows():

    # Cancelled orders have higher chance of failed/refunded payment.
    if order["order_status"] == "Cancelled":

        payment_status = np.random.choice(
            ["Failed", "Refunded"],
            p=[0.40, 0.60]
        )

    else:

        payment_status = np.random.choice(
            ["Success", "Failed"],
            p=[0.96, 0.04]
        )

    payment = {
        "payment_id": f"PAY{order['order_id'][1:]}",

        "order_id": order["order_id"],

        "payment_method": np.random.choice(
            payment_methods
        ),

        "payment_amount": round(
            order["net_amount"],
            2
        ),

        "payment_status": payment_status,

        "payment_datetime": order["order_datetime"]
    }

    payments.append(payment)


payments_df = pd.DataFrame(payments)


# ============================================================
# 10. GENERATE INVENTORY
# ============================================================

print("Generating inventory...")

inventory = []

for _, product in products_df.iterrows():

    stock_quantity = np.random.randint(
        10,
        500
    )

    reorder_level = np.random.randint(
        20,
        100
    )

    inventory_record = {
        "inventory_id": f"I{len(inventory) + 1:04d}",

        "product_id": product["product_id"],

        "warehouse": np.random.choice(
            warehouses
        ),

        "stock_quantity": stock_quantity,

        "reorder_level": reorder_level,

        "last_updated": pd.Timestamp.now()
    }

    inventory.append(inventory_record)


inventory_df = pd.DataFrame(inventory)


# ============================================================
# 11. GENERATE SHIPPING
# ============================================================

print("Generating shipping information...")

shipping = []

for _, order in orders_df.iterrows():

    warehouse = np.random.choice(
        warehouses
    )

    expected_days = np.random.randint(
        2,
        8
    )

    expected_delivery = (
        order["order_datetime"]
        + pd.Timedelta(days=expected_days)
    )

    # Different delivery outcomes
    delivery_status = np.random.choice(
        [
            "Delivered",
            "In Transit",
            "Delayed"
        ],
        p=[0.75, 0.15, 0.10]
    )

    if delivery_status == "Delivered":

        actual_delivery = (
            expected_delivery
            + pd.Timedelta(
                days=np.random.randint(-2, 3)
            )
        )

    elif delivery_status == "Delayed":

        actual_delivery = (
            expected_delivery
            + pd.Timedelta(
                days=np.random.randint(2, 6)
            )
        )

    else:

        actual_delivery = pd.NaT

    shipping_record = {
        "shipping_id": f"SH{order['order_id'][1:]}",

        "order_id": order["order_id"],

        "warehouse": warehouse,

        "shipping_cost": order["shipping_cost"],

        "expected_delivery": expected_delivery,

        "actual_delivery": actual_delivery,

        "delivery_status": delivery_status
    }

    shipping.append(shipping_record)


shipping_df = pd.DataFrame(shipping)


# ============================================================
# 12. GENERATE RETURNS
# ============================================================

print("Generating returns...")

returns = []

return_counter = 1

# Approximately 15% of completed orders are returned.

for _, order in orders_df.iterrows():

    if order["order_status"] == "Completed":

        should_return = np.random.random() < 0.15

        if should_return:

            return_record = {
                "return_id": f"R{return_counter:04d}",

                "order_id": order["order_id"],

                "product_id": order["product_id"],

                "return_reason": np.random.choice(
                    return_reasons
                ),

                "refund_amount": round(
                    order["net_amount"],
                    2
                ),

                "return_date": (
                    order["order_datetime"]
                    + pd.Timedelta(
                        days=np.random.randint(3, 20)
                    )
                )
            }

            returns.append(return_record)

            return_counter += 1


returns_df = pd.DataFrame(returns)


# ============================================================
# 13. SAVE ALL DATASETS
# ============================================================

print("\nSaving datasets...")


def save_data(df, filename):

    filepath = DATA_DIR / filename

    df.to_csv(
        filepath,
        index=False
    )

    print(
        f"Saved: {filename} "
        f"({len(df)} records)"
    )


save_data(
    suppliers_df,
    "suppliers.csv"
)

save_data(
    products_df,
    "products.csv"
)

save_data(
    customers_df,
    "customers.csv"
)

save_data(
    orders_df,
    "orders.csv"
)

save_data(
    payments_df,
    "payments.csv"
)

save_data(
    returns_df,
    "returns.csv"
)

save_data(
    inventory_df,
    "inventory.csv"
)

save_data(
    shipping_df,
    "shipping.csv"
)


# ============================================================
# 14. DATA SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DATA GENERATION COMPLETED")
print("=" * 60)

print(f"\nSuppliers : {len(suppliers_df)}")
print(f"Products  : {len(products_df)}")
print(f"Customers : {len(customers_df)}")
print(f"Orders    : {len(orders_df)}")
print(f"Payments  : {len(payments_df)}")
print(f"Returns   : {len(returns_df)}")
print(f"Inventory : {len(inventory_df)}")
print(f"Shipping  : {len(shipping_df)}")


# ============================================================
# 15. PROFIT STATISTICS
# ============================================================

print("\nProfit Statistics:")

print(
    orders_df["profit"].describe()
)


# ============================================================
# 16. BASIC BUSINESS INSIGHTS
# ============================================================

total_revenue = orders_df[
    orders_df["order_status"] == "Completed"
]["net_amount"].sum()

total_profit = orders_df[
    orders_df["order_status"] == "Completed"
]["profit"].sum()

total_orders = len(
    orders_df[
        orders_df["order_status"] == "Completed"
    ]
)

return_rate = (
    len(returns_df)
    / total_orders
    * 100
)


print("\n" + "=" * 60)
print("BASIC BUSINESS METRICS")
print("=" * 60)

print(
    f"\nTotal Revenue : Rs.{total_revenue:,.2f}"
)

print(
    f"Total Profit  : Rs.{total_profit:,.2f}"
)
print(
    f"Completed Orders : {total_orders}"
)

print(
    f"Return Rate : {return_rate:.2f}%"
)


# ============================================================
# 17. TOP PRODUCTS BY PROFIT
# ============================================================

completed_orders = orders_df[
    orders_df["order_status"] == "Completed"
]

product_profit = (
    completed_orders
    .groupby("product_id")["profit"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(5)
)

print("\nTop 5 Products by Profit:")

print(product_profit)


# ============================================================
# 18. PROJECT LOCATION
# ============================================================

print("\n" + "=" * 60)

print(
    f"All files saved in:\n{DATA_DIR}"
)

print("=" * 60)