
import sqlite3

# Connect to the existing database
connection = sqlite3.connect("movies.db")

# Read all SQL queries from the file
with open("queries.sql", "r", encoding="utf-8") as file:
    sql_content = file.read()

# Split the file into individual SQL queries
queries = [
    query.strip()
    for query in sql_content.split(";")
    if query.strip()
]

# Execute and display each query
for index, query in enumerate(queries, start=1):
    print(f"\n{'=' * 50}")
    print(f"QUERY {index}")
    print("=" * 50)

    cursor = connection.execute(query)
    results = cursor.fetchall()

    # Display column names
    columns = [description[0] for description in cursor.description]
    print(" | ".join(columns))

    # Display results
    for row in results[:10]:
        print(" | ".join(str(value) for value in row))

    if not results:
        print("No results found.")

connection.close()
print("\nAll queries executed successfully!")
