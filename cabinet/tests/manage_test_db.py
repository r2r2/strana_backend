import argparse
import psycopg2


def create_database(db_name, db_user, db_password):
    conn = psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_password,
        host="localhost",
        port=5433
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
    result = cursor.fetchone()
    if not result:
        cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")
    cursor.close()
    conn.close()


def drop_database(db_name, db_user, db_password):
    conn = psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_password,
        host="localhost",
        port=5433
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage test database.")
    parser.add_argument("action", choices=["create", "drop"])
    parser.add_argument("--db_name", required=True)
    parser.add_argument("--db_user", required=True)
    parser.add_argument("--db_password", required=True)
    args = parser.parse_args()

    if args.action == "create":
        create_database(args.db_name, args.db_user, args.db_password)
    elif args.action == "drop":
        drop_database(args.db_name, args.db_user, args.db_password)
