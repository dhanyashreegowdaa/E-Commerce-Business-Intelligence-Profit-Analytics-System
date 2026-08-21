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
print("E-COMMERCE RETURNS CSV TO MYSQL IMPORT")
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
# 4. IMPORT RETURNS
# ============================================================

file_path = DATA_DIR / "returns.csv"

print("\n" + "-" * 60)
print("Importing returns.csv")
print("-" * 60)


# ============================================================
# CHECK FILE
# ============================================================

if not file_path.exists():

    print(f"❌ File not found: {file_path}")

else:

    try:

        # ----------------------------------------------------
        # READ CSV
        # ----------------------------------------------------

        returns_df = pd.read_csv(file_path)

        print(f"Records found: {len(returns_df)}")

        print("\nCSV columns:")
        print(list(returns_df.columns))


        # ----------------------------------------------------
        # CONVERT RETURN DATE
        # ----------------------------------------------------

        returns_df["return_date"] = pd.to_datetime(
            returns_df["return_date"],
            errors="coerce"
        )


        # ----------------------------------------------------
        # CHECK INVALID DATES
        # ----------------------------------------------------

        invalid_dates = returns_df["return_date"].isna().sum()

        if invalid_dates > 0:

            print(
                f"⚠️ Invalid return dates found: {invalid_dates}"
            )

        else:

            print("✅ Return dates are valid.")


        # ----------------------------------------------------
        # REPLACE NaN WITH NONE
        # ----------------------------------------------------

        returns_df = returns_df.where(
            pd.notnull(returns_df),
            None
        )


        # ----------------------------------------------------
        # SQL INSERT
        #
        # ON DUPLICATE KEY UPDATE prevents duplicate
        # primary-key errors if the script is run again.
        # ----------------------------------------------------

        sql = """
            INSERT INTO returns
            (
                return_id,
                order_id,
                product_id,
                return_date,
                return_reason,
                refund_amount
            )
            VALUES (%s, %s, %s, %s, %s, %s)

            ON DUPLICATE KEY UPDATE

                order_id = VALUES(order_id),
                product_id = VALUES(product_id),
                return_date = VALUES(return_date),
                return_reason = VALUES(return_reason),
                refund_amount = VALUES(refund_amount)
        """


        # ----------------------------------------------------
        # PREPARE DATA
        # ----------------------------------------------------

        data = []

        for _, row in returns_df.iterrows():

            data.append(
                (
                    row["return_id"],
                    row["order_id"],
                    row["product_id"],
                    row["return_date"].to_pydatetime()
                    if row["return_date"] is not None
                    else None,
                    row["return_reason"],
                    row["refund_amount"]
                )
            )


        print(
            f"\nPreparing {len(data)} return records..."
        )


        # ----------------------------------------------------
        # INSERT INTO MYSQL
        # ----------------------------------------------------

        cursor.executemany(sql, data)

        connection.commit()

        print(
            "\n✅ Returns imported/updated successfully!"
        )

        print(
            f"Rows processed: {len(data)}"
        )


    except mysql.connector.Error as error:

        connection.rollback()

        print("\n❌ Error importing returns:")
        print(error)

    except Exception as error:

        connection.rollback()

        print("\n❌ Unexpected error:")
        print(error)


# ============================================================
# 5. CHECK RETURNS
# ============================================================

try:

    cursor.execute(
        "SELECT COUNT(*) FROM returns"
    )

    return_count = cursor.fetchone()[0]


    print("\n" + "=" * 60)
    print("RETURN IMPORT RESULT")
    print("=" * 60)

    print(
        f"Returns in MySQL: {return_count}"
    )


    # --------------------------------------------------------
    # SHOW FIRST 10 RETURNS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            return_id,
            order_id,
            product_id,
            return_date,
            return_reason,
            refund_amount
        FROM returns
        ORDER BY return_id
        LIMIT 10
        """
    )

    rows = cursor.fetchall()


    print("\nFirst 10 returns:")
    print("-" * 60)

    for row in rows:

        print(row)


except mysql.connector.Error as error:

    print("\n❌ Could not check returns table.")
    print(error)


# ============================================================
# 6. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n" + "=" * 60)
print("✅ RETURN IMPORT PROCESS COMPLETED")
print("=" * 60)