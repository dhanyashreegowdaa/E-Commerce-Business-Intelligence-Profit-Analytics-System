from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT AND DATA FOLDER
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"


# ============================================================
# 2. LOAD ALL DATASETS
# ============================================================

print("=" * 70)
print("REAL-TIME E-COMMERCE PROFIT - DATA VALIDATION")
print("=" * 70)


files = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "payments": "payments.csv",
    "returns": "returns.csv",
    "inventory": "inventory.csv",
    "shipping": "shipping.csv",
    "suppliers": "suppliers.csv"
}


datasets = {}


for name, filename in files.items():

    filepath = DATA_DIR / filename

    datasets[name] = pd.read_csv(filepath)

    print(
        f"\nLoaded {filename}: "
        f"{len(datasets[name])} rows"
    )


# ============================================================
# 3. DATASET STRUCTURE
# ============================================================

print("\n" + "=" * 70)
print("1. DATASET STRUCTURE")
print("=" * 70)


for name, df in datasets.items():

    print(f"\n{name.upper()}")

    print("-" * 50)

    print(
        f"Rows    : {df.shape[0]}"
    )

    print(
        f"Columns : {df.shape[1]}"
    )

    print(
        "Columns :",
        list(df.columns)
    )


# ============================================================
# 4. DATA TYPES
# ============================================================

print("\n" + "=" * 70)
print("2. DATA TYPES")
print("=" * 70)


for name, df in datasets.items():

    print(f"\n{name.upper()}")

    print(
        df.dtypes
    )


# ============================================================
# 5. MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("3. MISSING VALUES")
print("=" * 70)


for name, df in datasets.items():

    missing = df.isnull().sum()

    total_missing = missing.sum()

    print(
        f"\n{name.upper()}"
    )

    print(
        missing[missing > 0]
    )

    print(
        f"Total missing values: {total_missing}"
    )


# ============================================================
# 6. DUPLICATE RECORDS
# ============================================================

print("\n" + "=" * 70)
print("4. DUPLICATE RECORDS")
print("=" * 70)


for name, df in datasets.items():

    duplicates = df.duplicated().sum()

    print(
        f"{name.upper():12} : "
        f"{duplicates} duplicate rows"
    )


# ============================================================
# 7. PRIMARY KEY CHECK
# ============================================================

print("\n" + "=" * 70)
print("5. PRIMARY KEY VALIDATION")
print("=" * 70)


primary_keys = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "payments": "payment_id",
    "returns": "return_id",
    "inventory": "inventory_id",
    "shipping": "shipping_id",
    "suppliers": "supplier_id"
}


for name, key in primary_keys.items():

    df = datasets[name]

    duplicate_keys = df[key].duplicated().sum()

    missing_keys = df[key].isnull().sum()

    print(f"\n{name.upper()}")

    print(
        f"Duplicate {key}: "
        f"{duplicate_keys}"
    )

    print(
        f"Missing {key}: "
        f"{missing_keys}"
    )


# ============================================================
# 8. FOREIGN KEY VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("6. RELATIONSHIP / FOREIGN KEY VALIDATION")
print("=" * 70)


# Orders → Customers

invalid_customers = ~datasets["orders"]["customer_id"].isin(
    datasets["customers"]["customer_id"]
)

print(
    "\nOrders → Customers"
)

print(
    f"Invalid customer IDs: "
    f"{invalid_customers.sum()}"
)


# Orders → Products

invalid_products = ~datasets["orders"]["product_id"].isin(
    datasets["products"]["product_id"]
)

print(
    "\nOrders → Products"
)

print(
    f"Invalid product IDs: "
    f"{invalid_products.sum()}"
)


# Products → Suppliers

invalid_suppliers = ~datasets["products"]["supplier_id"].isin(
    datasets["suppliers"]["supplier_id"]
)

print(
    "\nProducts → Suppliers"
)

print(
    f"Invalid supplier IDs: "
    f"{invalid_suppliers.sum()}"
)


# Payments → Orders

invalid_payment_orders = ~datasets["payments"]["order_id"].isin(
    datasets["orders"]["order_id"]
)

print(
    "\nPayments → Orders"
)

print(
    f"Invalid order IDs: "
    f"{invalid_payment_orders.sum()}"
)


# Shipping → Orders

invalid_shipping_orders = ~datasets["shipping"]["order_id"].isin(
    datasets["orders"]["order_id"]
)

print(
    "\nShipping → Orders"
)

print(
    f"Invalid order IDs: "
    f"{invalid_shipping_orders.sum()}"
)


# Returns → Orders

invalid_return_orders = ~datasets["returns"]["order_id"].isin(
    datasets["orders"]["order_id"]
)

print(
    "\nReturns → Orders"
)

print(
    f"Invalid order IDs: "
    f"{invalid_return_orders.sum()}"
)


# Inventory → Products

invalid_inventory_products = ~datasets["inventory"]["product_id"].isin(
    datasets["products"]["product_id"]
)

print(
    "\nInventory → Products"
)

print(
    f"Invalid product IDs: "
    f"{invalid_inventory_products.sum()}"
)


# ============================================================
# 9. ORDER BUSINESS VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("7. ORDER BUSINESS VALIDATION")
print("=" * 70)


orders = datasets["orders"]


# Check negative quantity

negative_quantity = (
    orders["quantity"] < 0
).sum()

print(
    f"\nNegative quantities: "
    f"{negative_quantity}"
)


# Check zero quantity

zero_quantity = (
    orders["quantity"] == 0
).sum()

print(
    f"Zero quantities: "
    f"{zero_quantity}"
)


# Check negative selling price

negative_price = (
    orders["selling_price"] < 0
).sum()

print(
    f"Negative selling prices: "
    f"{negative_price}"
)


# Check negative net amount

negative_net_amount = (
    orders["net_amount"] < 0
).sum()

print(
    f"Negative net amounts: "
    f"{negative_net_amount}"
)


# ============================================================
# 10. PROFIT VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("8. PROFIT VALIDATION")
print("=" * 70)


# Calculate profit independently

calculated_profit = (
    orders["net_amount"]
    - orders["product_cost"]
    - orders["shipping_cost"]
    - orders["payment_fee"]
)


profit_difference = (
    orders["profit"]
    - calculated_profit
).abs()


incorrect_profit = (
    profit_difference > 0.01
).sum()


print(
    f"\nOrders with incorrect profit calculation: "
    f"{incorrect_profit}"
)


# ============================================================
# 11. LOSS-MAKING ORDERS
# ============================================================

loss_orders = orders[
    orders["profit"] < 0
]


print(
    f"\nLoss-making orders: "
    f"{len(loss_orders)}"
)


print(
    f"Percentage of loss-making orders: "
    f"{len(loss_orders) / len(orders) * 100:.2f}%"
)


# ============================================================
# 12. HIGH DISCOUNT ORDERS
# ============================================================

high_discount_orders = orders[
    orders["discount_percent"] >= 20
]


print(
    f"\nOrders with discount >= 20%: "
    f"{len(high_discount_orders)}"
)


# ============================================================
# 13. RETURN VALIDATION
# ============================================================

returns = datasets["returns"]


invalid_return_products = ~returns[
    "product_id"
].isin(
    products_id := datasets["products"]["product_id"]
)


print("\n" + "=" * 70)
print("9. RETURN VALIDATION")
print("=" * 70)


print(
    f"\nReturns with invalid product IDs: "
    f"{invalid_return_products.sum()}"
)


# ============================================================
# 14. INVENTORY VALIDATION
# ============================================================

inventory = datasets["inventory"]


negative_stock = (
    inventory["stock_quantity"] < 0
).sum()


print("\n" + "=" * 70)
print("10. INVENTORY VALIDATION")
print("=" * 70)


print(
    f"\nNegative stock quantities: "
    f"{negative_stock}"
)


low_stock = inventory[
    inventory["stock_quantity"]
    <= inventory["reorder_level"]
]


print(
    f"Products at or below reorder level: "
    f"{len(low_stock)}"
)


# ============================================================
# 15. FINAL VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION COMPLETED")
print("=" * 70)


print(
    """
The following areas were checked:

✓ Dataset structure
✓ Data types
✓ Missing values
✓ Duplicate records
✓ Primary keys
✓ Foreign keys
✓ Table relationships
✓ Order values
✓ Profit calculations
✓ Loss-making orders
✓ Discount levels
✓ Returns
✓ Inventory
"""
)

print("=" * 70)