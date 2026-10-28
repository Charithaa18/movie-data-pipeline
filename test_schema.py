
import sqlite3

# Connect to the database file (creates it if it doesn't exist)
connection = sqlite3.connect("movies.db")

# Enable foreign key enforcement
connection.execute("PRAGMA foreign_keys = ON")

# Read and execute the SQL schema
with open("schema.sql", "r", encoding="utf-8") as file:
    schema = file.read()

connection.executescript(schema)

# Check which tables were created
tables = connection.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

print("Tables created successfully:")
for table in tables:
    print("-", table[0])

connection.close()
