
import sqlite3


def run_data_quality_checks():
    """Check the quality and consistency of the movie database."""

    connection = sqlite3.connect("movies.db")

    try:
        checks = [
            (
                "Movies with missing IDs",
                "SELECT COUNT(*) FROM movies WHERE movie_id IS NULL"
            ),
            (
                "Movies with missing titles",
                """
                SELECT COUNT(*)
                FROM movies
                WHERE title IS NULL OR TRIM(title) = ''
                """
            ),
            (
                "Genres with missing names",
                """
                SELECT COUNT(*)
                FROM genres
                WHERE genre_name IS NULL OR TRIM(genre_name) = ''
                """
            ),
            (
                "Ratings with invalid movie references",
                """
                SELECT COUNT(*)
                FROM ratings AS r
                LEFT JOIN movies AS m ON r.movie_id = m.movie_id
                WHERE m.movie_id IS NULL
                """
            ),
            (
                "Movie-genre links with invalid movies",
                """
                SELECT COUNT(*)
                FROM movie_genres AS mg
                LEFT JOIN movies AS m ON mg.movie_id = m.movie_id
                WHERE m.movie_id IS NULL
                """
            ),
            (
                "Movie-genre links with invalid genres",
                """
                SELECT COUNT(*)
                FROM movie_genres AS mg
                LEFT JOIN genres AS g ON mg.genre_id = g.genre_id
                WHERE g.genre_id IS NULL
                """
            ),
        ]

        print("\nDATA QUALITY REPORT")
        print("=" * 50)

        has_issues = False

        for description, query in checks:
            count = connection.execute(query).fetchone()[0]
            status = "PASS" if count == 0 else "CHECK"

            if count > 0:
                has_issues = True

            print(f"{status}: {description}: {count}")

        # Check database foreign key consistency.
        foreign_key_issues = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if foreign_key_issues:
            has_issues = True

        print(
            f"{'PASS' if not foreign_key_issues else 'CHECK'}: "
            f"Foreign key violations: {len(foreign_key_issues)}"
        )

        print("=" * 50)
        print(
            "Overall result:",
            "ISSUES FOUND" if has_issues else "ALL CHECKS PASSED"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    run_data_quality_checks()
