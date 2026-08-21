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
print("SUPPLIERS CSV TO MYSQL IMPORT")
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
# 4. READ SUPPLIERS CSV
# ============================================================

file_path = DATA_DIR / "suppliers.csv"

print("\n" + "-" * 60)
print("Importing suppliers.csv")
print("-" * 60)

if not file_path.exists():

    print(f"❌ File not found: {file_path}")

    cursor.close()
    connection.close()
    exit()


df = pd.read_csv(file_path)

print(f"Records found: {len(df)}")


# ============================================================
# 5. CLEAN COLUMN NAMES
# ============================================================

df.columns = df.columns.str.strip().str.lower()

print("\nCSV columns found:")
print(df.columns.tolist())


# ============================================================
# 6. RENAME supplier_rating → rating
# ============================================================

if "supplier_rating" in df.columns:

    df.rename(
        columns={
            "supplier_rating": "rating"
        },
        inplace=True
    )


# ============================================================
# 7. CHECK REQUIRED CSV COLUMNS
# ============================================================

required_csv_columns = [
    "supplier_id",
    "supplier_name",
    "lead_time_days",
    "rating"
]

missing_columns = [
    column
    for column in required_csv_columns
    if column not in df.columns
]

if missing_columns:

    print("\n❌ Missing columns in suppliers.csv:")

    for column in missing_columns:
        print("   -", column)

    cursor.close()
    connection.close()
    exit()


# ============================================================
# 8. ADD CITY AND STATE AS NULL
# ============================================================

# Your CSV does not contain city or state.
# MySQL allows these columns to be NULL.

df["city"] = None
df["state"] = None


# ============================================================
# 9. REPLACE NaN WITH NONE
# ============================================================

df = df.where(pd.notnull(df), None)


# ============================================================
# 10. PREPARE SQL
# ============================================================

sql = """
    INSERT INTO suppliers
    (
        supplier_id,
        supplier_name,
        city,
        state,
        rating,
        lead_time_days
    )
    VALUES (%s, %s, %s, %s, %s, %s)
"""


# ============================================================
# 11. PREPARE DATA
# ============================================================

data = []

for _, row in df.iterrows():

    data.append(
        (
            row["supplier_id"],
            row["supplier_name"],
            row["city"],
            row["state"],
            row["rating"],
            row["lead_time_days"]
        )
    )


# ============================================================
# 12. INSERT INTO MYSQL
# ============================================================

try:

    cursor.executemany(sql, data)

    connection.commit()

    print(
        f"\n✅ Imported {cursor.rowcount} suppliers into MySQL"
    )

except mysql.connector.Error as error:

    connection.rollback()

    print("\n❌ Error importing suppliers:")
    print(error)


# ============================================================
# 13. CHECK SUPPLIER COUNT
# ============================================================

try:

    cursor.execute(
        "SELECT COUNT(*) FROM suppliers"
    )

    supplier_count = cursor.fetchone()[0]

    print("\n" + "=" * 60)
    print("SUPPLIER IMPORT RESULT")
    print("=" * 60)

    print(f"Suppliers in MySQL: {supplier_count}")

except mysql.connector.Error as error:

    print("\n❌ Could not check supplier count.")
    print(error)


# ============================================================
# 14. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n✅ Import process completed.")