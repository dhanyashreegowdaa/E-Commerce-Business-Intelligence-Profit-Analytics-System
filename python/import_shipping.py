import mysql.connector
import pandas as pd
from pathlib import Path
from getpass import getpass


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_ROOT / "data"

CSV_FILE = DATA_FOLDER / "shipping.csv"


print("=" * 60)
print("E-COMMERCE SHIPPING CSV TO MYSQL IMPORT")
print("=" * 60)

print(f"\nData folder:")
print(DATA_FOLDER)


# ============================================================
# 2. CHECK CSV FILE
# ============================================================

if not CSV_FILE.exists():
    print(f"\n❌ File not found: {CSV_FILE}")
    exit()

print(f"\n✅ Found: {CSV_FILE}")


# ============================================================
# 3. READ CSV
# ============================================================

try:
    df = pd.read_csv(CSV_FILE)

    print(f"\nRecords found: {len(df)}")

    print("\nCSV columns:")
    print(list(df.columns))

except Exception as error:
    print("\n❌ Could not read shipping.csv")
    print(error)
    exit()


# ============================================================
# 4. CLEAN COLUMN NAMES
# ============================================================

df.columns = df.columns.str.strip()

required_columns = [
    "shipping_id",
    "order_id",
    "warehouse",
    "shipping_cost",
    "expected_delivery",
    "actual_delivery",
    "delivery_status"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("\n❌ Missing columns:")
    print(missing_columns)
    exit()

print("\n✅ All required columns are present.")


# ============================================================
# 5. CONVERT DATES
# ============================================================

df["expected_delivery"] = pd.to_datetime(
    df["expected_delivery"],
    errors="coerce"
)

df["actual_delivery"] = pd.to_datetime(
    df["actual_delivery"],
    errors="coerce"
)

invalid_expected_dates = df["expected_delivery"].isna().sum()
invalid_actual_dates = df["actual_delivery"].isna().sum()

print(f"\nInvalid expected delivery dates: {invalid_expected_dates}")
print(f"Invalid actual delivery dates: {invalid_actual_dates}")


# ============================================================
# 6. MYSQL CONNECTION
# ============================================================

print("\nEnter your MySQL details:")

username = input("MySQL username [root]: ").strip()

if not username:
    username = "root"

password = getpass("MySQL password: ")

try:
    connection = mysql.connector.connect(
        host="localhost",
        user=username,
        password=password,
        database="ecommerce_profit"
    )

    print("\n✅ Connected to MySQL successfully!")

except mysql.connector.Error as error:
    print("\n❌ MySQL connection failed:")
    print(error)
    exit()


# ============================================================
# 7. INSERT / UPDATE SHIPPING DATA
# ============================================================

cursor = connection.cursor()

insert_query = """
INSERT INTO shipping
(
    shipping_id,
    order_id,
    warehouse,
    shipping_cost,
    expected_delivery,
    actual_delivery,
    delivery_status
)
VALUES
(
    %s, %s, %s, %s, %s, %s, %s
)
ON DUPLICATE KEY UPDATE
    order_id = VALUES(order_id),
    warehouse = VALUES(warehouse),
    shipping_cost = VALUES(shipping_cost),
    expected_delivery = VALUES(expected_delivery),
    actual_delivery = VALUES(actual_delivery),
    delivery_status = VALUES(delivery_status)
"""


records = []

for _, row in df.iterrows():

    expected_delivery = (
        row["expected_delivery"].to_pydatetime()
        if pd.notna(row["expected_delivery"])
        else None
    )

    actual_delivery = (
        row["actual_delivery"].to_pydatetime()
        if pd.notna(row["actual_delivery"])
        else None
    )

    records.append(
        (
            str(row["shipping_id"]),
            str(row["order_id"]),
            row["warehouse"],
            float(row["shipping_cost"]),
            expected_delivery,
            actual_delivery,
            row["delivery_status"]
        )
    )


print(f"\nPreparing {len(records)} shipping records...")


try:

    cursor.executemany(insert_query, records)

    connection.commit()

    print("\n✅ Shipping imported/updated successfully!")
    print(f"Rows processed: {len(records)}")

except mysql.connector.Error as error:

    connection.rollback()

    print("\n❌ Could not import shipping data:")
    print(error)

    cursor.close()
    connection.close()
    exit()


# ============================================================
# 8. VERIFY IMPORT
# ============================================================

try:

    cursor.execute("SELECT COUNT(*) FROM shipping")

    total_shipping = cursor.fetchone()[0]

    print("\n" + "=" * 60)
    print("SHIPPING IMPORT RESULT")
    print("=" * 60)

    print(f"\nShipping records in MySQL: {total_shipping}")

    cursor.execute("""
        SELECT
            shipping_id,
            order_id,
            warehouse,
            shipping_cost,
            expected_delivery,
            actual_delivery,
            delivery_status
        FROM shipping
        ORDER BY shipping_id
        LIMIT 10
    """)

    rows = cursor.fetchall()

    print("\nFirst 10 shipping records:\n")

    for row in rows:
        print(row)

except mysql.connector.Error as error:

    print("\n❌ Could not verify shipping table.")
    print(error)


# ============================================================
# 9. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n" + "=" * 60)
print("✅ SHIPPING IMPORT PROCESS COMPLETED")
print("=" * 60)