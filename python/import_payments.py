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
print("E-COMMERCE PAYMENTS CSV TO MYSQL IMPORT")
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
# 4. IMPORT PAYMENTS
# ============================================================

file_path = DATA_DIR / "payments.csv"

print("\n" + "-" * 60)
print("Importing payments.csv")
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

        payments_df = pd.read_csv(file_path)

        print(f"Records found: {len(payments_df)}")

        print("\nCSV columns:")
        print(list(payments_df.columns))


        # ----------------------------------------------------
        # RENAME CSV COLUMN
        # ----------------------------------------------------

        payments_df.rename(
            columns={
                "payment_datetime": "payment_date"
            },
            inplace=True
        )


        # ----------------------------------------------------
        # CONVERT PAYMENT DATE
        # ----------------------------------------------------

        payments_df["payment_date"] = pd.to_datetime(
            payments_df["payment_date"],
            errors="coerce"
        )


        # ----------------------------------------------------
        # CHECK INVALID DATES
        # ----------------------------------------------------

        invalid_dates = payments_df["payment_date"].isna().sum()

        if invalid_dates > 0:

            print(
                f"⚠️ Invalid payment dates found: {invalid_dates}"
            )

        else:

            print("✅ Payment dates are valid.")


        # ----------------------------------------------------
        # REPLACE NaN WITH NONE
        # ----------------------------------------------------

        payments_df = payments_df.where(
            pd.notnull(payments_df),
            None
        )


        # ----------------------------------------------------
        # SQL INSERT
        #
        # ON DUPLICATE KEY UPDATE prevents errors if
        # payments already exist.
        # ----------------------------------------------------

        sql = """
            INSERT INTO payments
            (
                payment_id,
                order_id,
                payment_date,
                payment_method,
                payment_status,
                payment_amount
            )
            VALUES (%s, %s, %s, %s, %s, %s)

            ON DUPLICATE KEY UPDATE

                order_id = VALUES(order_id),
                payment_date = VALUES(payment_date),
                payment_method = VALUES(payment_method),
                payment_status = VALUES(payment_status),
                payment_amount = VALUES(payment_amount)
        """


        # ----------------------------------------------------
        # PREPARE DATA
        # ----------------------------------------------------

        data = []

        for _, row in payments_df.iterrows():

            data.append(
                (
                    row["payment_id"],
                    row["order_id"],
                    row["payment_date"].to_pydatetime()
                    if row["payment_date"] is not None
                    else None,
                    row["payment_method"],
                    row["payment_status"],
                    row["payment_amount"]
                )
            )


        print(
            f"\nPreparing {len(data)} payment records..."
        )


        # ----------------------------------------------------
        # INSERT INTO MYSQL
        # ----------------------------------------------------

        cursor.executemany(sql, data)

        connection.commit()

        print(
            "\n✅ Payments imported/updated successfully!"
        )

        print(
            f"Rows processed: {len(data)}"
        )


    except mysql.connector.Error as error:

        connection.rollback()

        print("\n❌ Error importing payments:")
        print(error)

    except Exception as error:

        connection.rollback()

        print("\n❌ Unexpected error:")
        print(error)


# ============================================================
# 5. CHECK PAYMENTS
# ============================================================

try:

    cursor.execute(
        "SELECT COUNT(*) FROM payments"
    )

    payment_count = cursor.fetchone()[0]


    print("\n" + "=" * 60)
    print("PAYMENT IMPORT RESULT")
    print("=" * 60)

    print(
        f"Payments in MySQL: {payment_count}"
    )


    # --------------------------------------------------------
    # SHOW FIRST 10 PAYMENTS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            payment_id,
            order_id,
            payment_date,
            payment_method,
            payment_status,
            payment_amount
        FROM payments
        ORDER BY payment_id
        LIMIT 10
        """
    )

    rows = cursor.fetchall()


    print("\nFirst 10 payments:")
    print("-" * 60)

    for row in rows:

        print(row)


except mysql.connector.Error as error:

    print("\n❌ Could not check payments table.")
    print(error)


# ============================================================
# 6. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n" + "=" * 60)
print("✅ PAYMENT IMPORT PROCESS COMPLETED")
print("=" * 60)
