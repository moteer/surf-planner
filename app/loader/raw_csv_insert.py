import pandas as pd
import pymysql
import numpy as np
from urllib.parse import urlparse

def clean_dataframe(df):
    df.columns = [col.strip().replace('%', 'percent')
                  .replace(' ', '_')
                  .replace('(', '')
                  .replace(')', '')
                  .replace('-', '_')
                  .lower() for col in df.columns]

    def clean_value(val):
        try:
            if isinstance(val, float) and np.isnan(val):
                return None
            if pd.isna(val):
                return None
        except Exception:
            pass
        return val

    return df.applymap(clean_value)

def create_table_from_df(df, table_name, connection):
    columns_sql = [f"`{col}` TEXT NULL" for col in df.columns]
    columns_block = ",\n  ".join(columns_sql)
    create_stmt = f"CREATE TABLE `{table_name}` (\n  {columns_block}\n) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;"

    with connection.cursor() as cursor:
        print(f"🧨 Dropping existing table `{table_name}` (if any)...")
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        print(f"🛠️ Creating new table `{table_name}`...")
        cursor.execute(create_stmt)
        connection.commit()
        print("✅ Table created.")

def insert_dataframe_raw(df, table_name, connection):
    if df.empty:
        print("🚫 DataFrame is empty. Nothing to insert.")
        return

    with connection.cursor() as cursor:
        columns = ', '.join(f"`{col}`" for col in df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

        def to_safe_tuple(row):
            return tuple(None if isinstance(x, float) and np.isnan(x) else x for x in row)

        values = [to_safe_tuple(row) for row in df.values.tolist()]

        print(f"📥 Inserting {len(values)} records into `{table_name}`...")
        cursor.executemany(sql, values)
        connection.commit()
        print("✅ Insert complete.")

def parse_mysql_url(mysql_url):
    parsed = urlparse(mysql_url.replace("mysql+pymysql://", "mysql://"))
    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "db": parsed.path.lstrip("/")
    }

def main():
    mysql_url = "mysql+pymysql://admin:admin@localhost:3306/sea_natives_surfplanner"
    csv_path = "csvs/2025-05-26-surf-plan_evening.csv"
    table_name = "bookings"

    print(f"📂 Loading CSV from '{csv_path}'...")
    df = pd.read_csv(csv_path)

    print("🧼 Cleaning data...")
    df = clean_dataframe(df)

    print("🧻 Remove empty columns...")
    print_empty_columns(df)


    print("🐷 Column names:")
    print(df.columns.values)

    print(f"🔌 Connecting to MySQL...")
    conn_params = parse_mysql_url(mysql_url)
    connection = pymysql.connect(
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        **conn_params
    )

    try:
        create_table_from_df(df, table_name, connection)
        insert_dataframe_raw(df, table_name, connection)
    finally:
        connection.close()


def print_empty_columns(df):
    # 🕵️ Identify columns with only NULLs
    null_only_cols = df.columns[df.isnull().all()].tolist()
    if null_only_cols:
        print("🕳️ Columns that are entirely NULL:")
        for col in null_only_cols:
            print(f"  - {col}")
    else:
        print("✅ No completely NULL columns.")

    df = df.drop(columns=null_only_cols)
    print(f"🧹 Dropped {len(null_only_cols)} all-null columns.")

    print("💯columns left")
    print(len(df.columns))

if __name__ == "__main__":
    main()
