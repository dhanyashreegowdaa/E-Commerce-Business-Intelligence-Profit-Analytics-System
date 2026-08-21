from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "data"

CLEANED_DIR = DATA_DIR / "cleaned"

CLEANED_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("REAL-TIME E-COMMERCE PROFIT - DATA CLEANING")
print("=" * 70)


# ============================================================
# 2. LOAD DATASETS
# ============================================================

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
        f"Loaded {filename}: "
        f"{len(datasets[name])} rows"
    )


# ============================================================
# 3. REMOVE DUPLICATE RECORDS
# ============================================================

print("\n" + "=" * 70)
print("REMOVING DUPLICATES")
print("=" * 70)


for name in datasets:

    before = len(datasets[name])

    datasets[name] = datasets[name].drop_duplicates()

    after = len(datasets[name])

    removed = before - after

    print(
        f"{name.upper():12} : "
        f"{removed} duplicates removed"
    )


# ============================================================
# 4. HANDLE MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("HANDLING MISSING VALUES")
print("=" * 70)


for name, df in datasets.items():

    missing_before = df.isnull().sum().sum()

    # Numeric columns → fill with median
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        if df[column].isnull().any():

            df[column] = df[column].fillna(
                df[column].median()
            )

    # Text columns → fill with "Unknown"
    text_columns = df.select_dtypes(
        include="object"
    ).columns

    for column in text_columns:

        if df[column].isnull().any():

            df[column] = df[column].fillna(
                "Unknown"
            )

    missing_after = df.isnull().sum().sum()

    print(
        f"{name.upper():12} : "
        f"{missing_before} → {missing_after} missing values"
    )


# ============================================================
# 5. STANDARDIZE TEXT COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("STANDARDIZING TEXT DATA")
print("=" * 70)


for name, df in datasets.items():

    text_columns = df.select_dtypes(
        include="object"
    ).columns

    for column in text_columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )


print("Text formatting completed.")


# ============================================================
# 6. CONVERT DATE COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("CONVERTING DATE COLUMNS")
print("=" * 70)


date_columns = {
    "orders": ["order_date"],
    "payments": ["payment_date"],
    "returns": ["return_date"],
    "shipping": ["shipping_date"],
    "customers": ["registration_date"]
}


for dataset_name, columns in date_columns.items():

    df = datasets[dataset_name]

    for column in columns:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            print(
                f"{dataset_name}.{column} "
                f"converted to datetime"
            )


# ============================================================
# 7. REMOVE INVALID ORDER VALUES
# ============================================================

print("\n" + "=" * 70)
print("CHECKING ORDER VALUES")
print("=" * 70)


orders = datasets["orders"]


before = len(orders)


orders = orders[
    (orders["quantity"] > 0)
    &
    (orders["selling_price"] >= 0)
    &
    (orders["net_amount"] >= 0)
]


after = len(orders)


print(
    f"Invalid orders removed: "
    f"{before - after}"
)


datasets["orders"] = orders


# ============================================================
# 8. ROUND FINANCIAL VALUES
# ============================================================

print("\n" + "=" * 70)
print("ROUNDING FINANCIAL VALUES")
print("=" * 70)


financial_columns = [
    "selling_price",
    "discount_amount",
    "net_amount",
    "product_cost",
    "shipping_cost",
    "payment_fee",
    "profit"
]


orders = datasets["orders"]


for column in financial_columns:

    if column in orders.columns:

        orders[column] = orders[column].round(2)


datasets["orders"] = orders


print("Financial values rounded to 2 decimal places.")


# ============================================================
# 9. CREATE PROFIT MARGIN
# ============================================================

print("\n" + "=" * 70)
print("CREATING PROFIT MARGIN")
print("=" * 70)


orders = datasets["orders"]


orders["profit_margin"] = (
    orders["profit"]
    /
    orders["net_amount"]
    * 100
)


orders["profit_margin"] = (
    orders["profit_margin"]
    .replace([float("inf"), -float("inf")], 0)
    .fillna(0)
    .round(2)
)


datasets["orders"] = orders


print("Profit margin column created.")


# ============================================================
# 10. CREATE PROFIT STATUS
# ============================================================

orders["profit_status"] = orders["profit"].apply(
    lambda x:
        "Loss"
        if x < 0
        else "Profit"
)


datasets["orders"] = orders


print("Profit status column created.")


# ============================================================
# 11. CREATE DISCOUNT CATEGORY
# ============================================================

def classify_discount(discount):

    if discount == 0:
        return "No Discount"

    elif discount < 10:
        return "Low Discount"

    elif discount < 20:
        return "Medium Discount"

    else:
        return "High Discount"


orders["discount_category"] = (
    orders["discount_percent"]
    .apply(classify_discount)
)


datasets["orders"] = orders


print("Discount category created.")


# ============================================================
# 12. SAVE CLEANED DATA
# ============================================================

print("\n" + "=" * 70)
print("SAVING CLEANED DATA")
print("=" * 70)


for name, df in datasets.items():

    filepath = CLEANED_DIR / f"{name}_cleaned.csv"

    df.to_csv(
        filepath,
        index=False
    )

    print(
        f"Saved: {filepath.name} "
        f"({len(df)} rows)"
    )


# ============================================================
# 13. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DATA CLEANING COMPLETED")
print("=" * 70)


print(
    f"\nCleaned files saved in:\n"
    f"{CLEANED_DIR}"
)


print("\nOrders now contain additional analytical columns:")

print(
    """
✓ profit_margin
✓ profit_status
✓ discount_category
"""
)


print("=" * 70)