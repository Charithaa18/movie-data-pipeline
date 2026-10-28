
import sqlite3

connection = sqlite3.connect("movies.db")

tables = ["movies", "genres", "movie_genres", "ratings", "omdb_cache"]

for table in tables:
    count = connection.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count} rows")

successful = connection.execute(
    "SELECT COUNT(*) FROM omdb_cache WHERE status = 'success'"
).fetchone()[0]

not_found = connection.execute(
    "SELECT COUNT(*) FROM omdb_cache WHERE status = 'not_found'"
).fetchone()[0]

print(f"\nSuccessful OMDb lookups: {successful}")
print(f"Movies not found in OMDb: {not_found}")

connection.close()

