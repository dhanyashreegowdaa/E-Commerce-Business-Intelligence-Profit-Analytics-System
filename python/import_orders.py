import mysql.connector
import pandas as pd
from pathlib import Path
from getpass import getpass


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

print("=" * 70)
print("E-COMMERCE ORDERS CSV TO MYSQL IMPORT")
print("=" * 70)

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
# 4. READ ORDERS CSV
# ============================================================

file_path = DATA_DIR / "orders.csv"

print("\n" + "-" * 70)
print("Importing orders.csv")
print("-" * 70)


if not file_path.exists():

    print(f"❌ File not found: {file_path}")

    cursor.close()
    connection.close()
    exit()


# Read CSV
try:

    orders_df = pd.read_csv(file_path)

except Exception as error:

    print("❌ Could not read orders.csv")
    print(error)

    cursor.close()
    connection.close()
    exit()


print(f"\nRecords found: {len(orders_df)}")

print("\nCSV columns:")
print(list(orders_df.columns))


# ============================================================
# 5. CLEAN COLUMN NAMES
# ============================================================

orders_df.columns = (
    orders_df.columns
    .str.strip()
    .str.lower()
)


# ============================================================
# 6. RENAME CSV COLUMNS TO MATCH MYSQL
# ============================================================

column_mapping = {

    # CSV name              MySQL name
    "order_datetime": "order_date",

}

orders_df.rename(
    columns=column_mapping,
    inplace=True
)


print("\nColumns after mapping:")
print(list(orders_df.columns))


# ============================================================
# 7. GET MYSQL ORDERS TABLE COLUMNS
# ============================================================

try:

    cursor.execute("DESCRIBE orders")

    mysql_columns_info = cursor.fetchall()

    mysql_columns = [
        row[0]
        for row in mysql_columns_info
    ]

    print("\nExisting MySQL orders columns:")
    print(mysql_columns)

except mysql.connector.Error as error:

    print("\n❌ Could not read orders table structure.")
    print(error)

    cursor.close()
    connection.close()
    exit()


# ============================================================
# 8. ADD MISSING COLUMNS
# ============================================================

print("\nChecking for missing columns...")


# Columns that should be decimal
decimal_columns = {

    "selling_price",
    "discount_percent",
    "gross_amount",
    "discount_amount",
    "net_amount",
    "product_cost",
    "shipping_cost",
    "payment_fee",
    "profit"

}


# Columns that should be integers
integer_columns = {

    "quantity"

}


# Columns that should be datetime
datetime_columns = {

    "order_date"

}


for column in orders_df.columns:

    if column in mysql_columns:

        continue

    print(f"\n⚠️ Missing MySQL column: {column}")

    # Decide data type
    if column in decimal_columns:

        sql_type = "DECIMAL(12,2)"

    elif column in integer_columns:

        sql_type = "INT"

    elif column in datetime_columns:

        sql_type = "DATETIME"

    else:

        sql_type = "VARCHAR(50)"

    alter_sql = f"""
        ALTER TABLE orders
        ADD COLUMN `{column}` {sql_type}
    """

    try:

        cursor.execute(alter_sql)

        connection.commit()

        print(
            f"✅ Added column `{column}` as {sql_type}"
        )

    except mysql.connector.Error as error:

        print(
            f"❌ Could not add column `{column}`"
        )

        print(error)


# ============================================================
# 9. GET UPDATED MYSQL COLUMNS
# ============================================================

try:

    cursor.execute("DESCRIBE orders")

    mysql_columns_info = cursor.fetchall()

    mysql_columns = [
        row[0]
        for row in mysql_columns_info
    ]

except mysql.connector.Error as error:

    print("\n❌ Could not refresh table structure.")
    print(error)

    cursor.close()
    connection.close()
    exit()


print("\nUpdated MySQL columns:")
print(mysql_columns)


# ============================================================
# 10. KEEP ONLY COMMON COLUMNS
# ============================================================

common_columns = [
    column
    for column in orders_df.columns
    if column in mysql_columns
]


print("\nColumns that will be imported:")
print(common_columns)


# Check order_id
if "order_id" not in common_columns:

    print("\n❌ ERROR: order_id is missing.")

    cursor.close()
    connection.close()
    exit()


# ============================================================
# 11. PREPARE DATA
# ============================================================

orders_df = orders_df[common_columns].copy()


# Convert order_date
if "order_date" in orders_df.columns:

    orders_df["order_date"] = pd.to_datetime(
        orders_df["order_date"],
        errors="coerce"
    )


# Replace NaN with None
orders_df = orders_df.where(
    pd.notnull(orders_df),
    None
)


print(
    f"\nPreparing {len(orders_df)} order records..."
)


# ============================================================
# 12. CREATE INSERT / UPDATE QUERY
# ============================================================

column_names = ", ".join(
    f"`{column}`"
    for column in common_columns
)

placeholders = ", ".join(
    ["%s"] * len(common_columns)
)


# Update every column except order_id
update_columns = [
    column
    for column in common_columns
    if column != "order_id"
]


update_statement = ", ".join(
    f"`{column}` = VALUES(`{column}`)"
    for column in update_columns
)


sql = f"""
    INSERT INTO orders
    ({column_names})
    VALUES ({placeholders})
    ON DUPLICATE KEY UPDATE
    {update_statement}
"""


# ============================================================
# 13. PREPARE DATA LIST
# ============================================================

data = []

for _, row in orders_df.iterrows():

    values = []

    for column in common_columns:

        value = row[column]

        # Convert pandas timestamp to Python datetime
        if pd.isna(value):

            value = None

        elif isinstance(
            value,
            pd.Timestamp
        ):

            value = value.to_pydatetime()

        values.append(value)

    data.append(tuple(values))


# ============================================================
# 14. INSERT INTO MYSQL
# ============================================================

try:

    cursor.executemany(
        sql,
        data
    )

    connection.commit()

    print(
        "\n✅ Orders imported/updated successfully!"
    )

    print(
        f"Rows processed: {len(data)}"
    )

except mysql.connector.Error as error:

    connection.rollback()

    print(
        "\n❌ Error importing orders:"
    )

    print(error)


# ============================================================
# 15. CHECK ORDER COUNT
# ============================================================

try:

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )

    order_count = cursor.fetchone()[0]

    print("\n" + "=" * 70)
    print("ORDER IMPORT RESULT")
    print("=" * 70)

    print(
        f"Orders in MySQL: {order_count}"
    )


except mysql.connector.Error as error:

    print(
        "\n❌ Could not check orders table."
    )

    print(error)


# ============================================================
# 16. DISPLAY FIRST 10 ORDERS
# ============================================================

try:

    cursor.execute(
        "SELECT * FROM orders LIMIT 10"
    )

    rows = cursor.fetchall()

    print("\nFirst 10 orders:")
    print("-" * 70)

    for row in rows:

        print(row)


except mysql.connector.Error as error:

    print(
        "\n❌ Could not display orders."
    )

    print(error)


# ============================================================
# 17. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()


print("\n" + "=" * 70)
print("✅ ORDER IMPORT PROCESS COMPLETED")
print("=" * 70)