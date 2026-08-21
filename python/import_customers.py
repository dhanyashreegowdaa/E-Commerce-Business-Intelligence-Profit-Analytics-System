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
print("CUSTOMERS CSV TO MYSQL IMPORT")
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
# 4. READ CUSTOMERS CSV
# ============================================================

file_path = DATA_DIR / "customers.csv"

print("\n" + "-" * 60)
print("Importing customers.csv")
print("-" * 60)

if not file_path.exists():

    print(f"❌ File not found: {file_path}")

    cursor.close()
    connection.close()

    exit()


customers_df = pd.read_csv(file_path)

print(f"Records found: {len(customers_df)}")


# ============================================================
# 5. SHOW CSV COLUMNS
# ============================================================

print("\nCSV columns found:")
print(list(customers_df.columns))


# ============================================================
# 6. CHECK REQUIRED CSV COLUMNS
# ============================================================

required_csv_columns = [
    "customer_id",
    "customer_name",
    "city",
    "state",
    "customer_segment",
    "signup_date"
]

missing_columns = [
    column
    for column in required_csv_columns
    if column not in customers_df.columns
]

if missing_columns:

    print("\n❌ Missing columns in customers.csv:")

    for column in missing_columns:
        print(f"   - {column}")

    print("\nExpected CSV columns:")
    print(required_csv_columns)

    cursor.close()
    connection.close()

    exit()


# ============================================================
# 7. CLEAN DATA
# ============================================================

customers_df = customers_df.where(
    pd.notnull(customers_df),
    None
)


# ============================================================
# 8. INSERT INTO MYSQL
# ============================================================

# NOTE:
# CSV has signup_date
# MySQL table has registration_date
#
# CSV does NOT have email
# Therefore email will be inserted as NULL
#
# CSV customer_segment is not present in MySQL table,
# so it is ignored.

sql = """
    INSERT INTO customers
    (
        customer_id,
        customer_name,
        email,
        city,
        state,
        registration_date
    )
    VALUES (%s, %s, %s, %s, %s, %s)
"""


# ============================================================
# 9. PREPARE DATA
# ============================================================

data = []

for _, row in customers_df.iterrows():

    data.append(
        (
            row["customer_id"],
            row["customer_name"],
            None,                       # email is not in CSV
            row["city"],
            row["state"],
            row["signup_date"]           # signup_date → registration_date
        )
    )


# ============================================================
# 10. IMPORT DATA
# ============================================================

try:

    cursor.executemany(sql, data)

    connection.commit()

    print(
        f"\n✅ Imported {cursor.rowcount} customers into MySQL"
    )

except mysql.connector.Error as error:

    connection.rollback()

    print("\n❌ Error importing customers:")
    print(error)


# ============================================================
# 11. CHECK RESULT
# ============================================================

cursor.execute("SELECT COUNT(*) FROM customers")

customer_count = cursor.fetchone()[0]

print("\n" + "=" * 60)
print("CUSTOMER IMPORT RESULT")
print("=" * 60)

print(f"Customers in MySQL: {customer_count}")


# ============================================================
# 12. SHOW SAMPLE DATA
# ============================================================

cursor.execute("""
    SELECT
        customer_id,
        customer_name,
        email,
        city,
        state,
        registration_date
    FROM customers
    LIMIT 5
""")

rows = cursor.fetchall()

print("\nSample customers:")

for row in rows:
    print(row)


# ============================================================
# 13. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n✅ Import process completed.")