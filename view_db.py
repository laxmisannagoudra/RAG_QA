import sqlite3

conn = sqlite3.connect("data/metadata.db")

for table in ["documents", "chunks", "queries"]:
    print("\n==", table, "==")
    for row in conn.execute(f"SELECT * FROM {table} LIMIT 5"):
        print(str(row)[:150])

conn.close()