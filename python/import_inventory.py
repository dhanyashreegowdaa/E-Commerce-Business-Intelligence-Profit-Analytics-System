import mysql.connector
import pandas as pd
from pathlib import Path
from getpass import getpass


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

print("=" * 60)
print("INVENTORY CSV TO MYSQL IMPORT")
print("=" * 60)

print("\nData folder:")
print(DATA_DIR)


# ============================================================
# 2. MYSQL LOGIN
# ============================================================

print("\nEnter your MySQL details.")

mysql_user = input("MySQL username [root]: ").strip()

if mysql_user == "":
    mysql_user = "root"

mysql_password = getpass("MySQL password: ")


# ============================================================
# 3. CONNECT TO MYSQL
# ============================================================

try:

    connection = mysql.connector.connect(
        host="localhost",
        user=mysql_user,
        password=mysql_password,
        database="ecommerce_profit"
    )

    cursor = connection.cursor()

    print("\n✅ Connected to MySQL successfully!")

except mysql.connector.Error as error:

    print("\n❌ MySQL connection failed.")
    print(error)
    exit()


# ============================================================
# 4. READ INVENTORY CSV
# ============================================================

file_path = DATA_DIR / "inventory.csv"

print("\n" + "-" * 60)
print("Importing inventory.csv")
print("-" * 60)

if not file_path.exists():

    print(f"❌ File not found: {file_path}")

    cursor.close()
    connection.close()

    exit()


df = pd.read_csv(file_path)

print(f"Records found: {len(df)}")


# ============================================================
# 5. DISPLAY CSV COLUMNS
# ============================================================

print("\nCSV columns found:")

print(list(df.columns))


# ============================================================
# 6. RENAME COLUMN
# ============================================================

if "last_updated" in df.columns:

    df.rename(
        columns={
            "last_updated": "last_restock_date"
        },
        inplace=True
    )


# ============================================================
# 7. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "inventory_id",
    "product_id",
    "stock_quantity",
    "reorder_level",
    "last_restock_date"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print("\n❌ Missing columns in inventory.csv:")

    for column in missing_columns:
        print(f"   - {column}")

    print("\nExpected columns:")
    print(required_columns)

    cursor.close()
    connection.close()

    exit()


# ============================================================
# 8. SELECT ONLY MYSQL COLUMNS
# ============================================================

df = df[required_columns]


# ============================================================
# 9. REPLACE NaN WITH NONE
# ============================================================

df = df.where(pd.notnull(df), None)


# ============================================================
# 10. SQL INSERT
# ============================================================

sql = """
    INSERT INTO inventory
    (
        inventory_id,
        product_id,
        stock_quantity,
        reorder_level,
        last_restock_date
    )
    VALUES (%s, %s, %s, %s, %s)
"""


# ============================================================
# 11. PREPARE DATA
# ============================================================

data = []

for _, row in df.iterrows():

    data.append(
        (
            row["inventory_id"],
            row["product_id"],
            row["stock_quantity"],
            row["reorder_level"],
            row["last_restock_date"]
        )
    )


# ============================================================
# 12. IMPORT DATA
# ============================================================

try:

    cursor.executemany(sql, data)

    connection.commit()

    print(
        f"\n✅ Imported {cursor.rowcount} inventory records into MySQL"
    )

except mysql.connector.Error as error:

    connection.rollback()

    print("\n❌ Error importing inventory:")
    print(error)


# ============================================================
# 13. CHECK INVENTORY COUNT
# ============================================================

cursor.execute("SELECT COUNT(*) FROM inventory")

inventory_count = cursor.fetchone()[0]

print("\n" + "=" * 60)
print("INVENTORY IMPORT RESULT")
print("=" * 60)

print(f"Inventory records in MySQL: {inventory_count}")


# ============================================================
# 14. SHOW SAMPLE DATA
# ============================================================

cursor.execute("""
    SELECT
        inventory_id,
        product_id,
        stock_quantity,
        reorder_level,
        last_restock_date
    FROM inventory
    LIMIT 5
""")

rows = cursor.fetchall()

print("\nSample inventory records:")

for row in rows:
    print(row)


# ============================================================
# 15. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n✅ Import process completed.")