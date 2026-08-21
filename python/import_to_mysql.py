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
print("E-COMMERCE CSV TO MYSQL IMPORT")
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
# 4. IMPORT PRODUCTS
# ============================================================

file_path = DATA_DIR / "products.csv"

print("\n" + "-" * 60)
print("Importing products.csv")
print("-" * 60)


# ============================================================
# 5. CHECK FILE
# ============================================================

if not file_path.exists():

    print(f"❌ File not found: {file_path}")

else:

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    try:

        products_df = pd.read_csv(file_path)

        print(f"Records found: {len(products_df)}")

    except Exception as error:

        print("❌ Could not read products.csv")
        print(error)

        cursor.close()
        connection.close()
        exit()


    # --------------------------------------------------------
    # Display CSV columns
    # --------------------------------------------------------

    print("\nCSV columns:")

    print(products_df.columns.tolist())


    # --------------------------------------------------------
    # Rename cost_price → product_cost
    # --------------------------------------------------------

    if "cost_price" in products_df.columns:

        products_df.rename(
            columns={
                "cost_price": "product_cost"
            },
            inplace=True
        )


    # --------------------------------------------------------
    # Replace NaN with None
    # --------------------------------------------------------

    products_df = products_df.where(
        pd.notnull(products_df),
        None
    )


    # ========================================================
    # 6. CHECK REQUIRED COLUMNS
    # ========================================================

    required_columns = [
        "product_id",
        "product_name",
        "category",
        "supplier_id",
        "product_cost",
        "selling_price"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in products_df.columns
    ]


    if missing_columns:

        print("\n❌ Missing columns in CSV:")

        for column in missing_columns:
            print("-", column)

        cursor.close()
        connection.close()
        exit()


    # ========================================================
    # 7. SQL INSERT / UPDATE
    # ========================================================

    sql = """
        INSERT INTO products
        (
            product_id,
            product_name,
            category,
            supplier_id,
            product_cost,
            selling_price
        )
        VALUES (%s, %s, %s, %s, %s, %s)

        ON DUPLICATE KEY UPDATE

            product_name = VALUES(product_name),
            category = VALUES(category),
            supplier_id = VALUES(supplier_id),
            product_cost = VALUES(product_cost),
            selling_price = VALUES(selling_price)
    """


    # ========================================================
    # 8. PREPARE DATA
    # ========================================================

    data = []

    for _, row in products_df.iterrows():

        data.append(
            (
                row["product_id"],
                row["product_name"],
                row["category"],
                row["supplier_id"],
                row["product_cost"],
                row["selling_price"]
            )
        )


    print(f"\nPreparing {len(data)} records...")


    # ========================================================
    # 9. INSERT INTO MYSQL
    # ========================================================

    try:

        cursor.executemany(sql, data)

        connection.commit()

        print("\n✅ Products imported/updated successfully!")

        print(
            f"Rows processed: {len(data)}"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        print("\n❌ Error importing products:")
        print(error)


# ============================================================
# 10. CHECK PRODUCTS
# ============================================================

try:

    cursor.execute(
        "SELECT COUNT(*) FROM products"
    )

    product_count = cursor.fetchone()[0]


    print("\n" + "=" * 60)
    print("PRODUCT IMPORT RESULT")
    print("=" * 60)

    print(
        f"Products in MySQL: {product_count}"
    )


except mysql.connector.Error as error:

    print("\n❌ Could not check products table.")
    print(error)


# ============================================================
# 11. DISPLAY PRODUCTS
# ============================================================

try:

    cursor.execute("""
        SELECT
            product_id,
            product_name,
            category,
            supplier_id,
            product_cost,
            selling_price
        FROM products
        ORDER BY product_id
        LIMIT 10
    """)

    rows = cursor.fetchall()


    print("\nFirst 10 products:")
    print("-" * 60)

    for row in rows:

        print(row)


except mysql.connector.Error as error:

    print("\n❌ Could not display products.")
    print(error)


# ============================================================
# 12. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n" + "=" * 60)
print("✅ IMPORT PROCESS COMPLETED")
print("=" * 60)