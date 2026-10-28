import os
import time
import requests
import re
import argparse
import json
import sqlite3
import pandas as pd


def extract_csv_data():
    """Read movie and rating data from CSV files."""

    movies = pd.read_csv("movies.csv")
    ratings = pd.read_csv("ratings.csv")

    print(f"Movies extracted: {len(movies)}")
    print(f"Ratings extracted: {len(ratings)}")

    return movies, ratings



def fetch_movie_details(title, year=None):
    """Fetch additional details for one movie from OMDb."""

    api_key = os.getenv("OMDB_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OMDB_API_KEY is not set. Configure your API key before running ETL."
        )

    params = {
        "apikey": api_key,
        "t": title
    }

    if year is not None:
        params["y"] = year

    try:
        response = requests.get(
            "https://www.omdbapi.com/",
            params=params,
            timeout=15
        )
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError as error:
            raise RuntimeError(
                "OMDb returned an invalid JSON response."
            ) from error

        if not isinstance(data, dict):
            raise RuntimeError("OMDb returned an unexpected response format.")

        if data.get("Response") != "True":
            error_message = data.get("Error", "Unknown OMDb error")

            if error_message.lower() == "movie not found!":
                print(f"Movie not found: {title}")
                return None

            if "invalid api key" in error_message.lower():
                raise RuntimeError(
                    "OMDb rejected the API key. Check OMDB_API_KEY."
                )

            if "limit" in error_message.lower() or "request" in error_message.lower():
                raise RuntimeError(
                    f"OMDb API error; check the API quota and key status: "
                    f"{error_message}"
                )

            raise RuntimeError(f"OMDb API error: {error_message}")

        return {
            "director": data.get("Director"),
            "plot": data.get("Plot"),
            "release_year": data.get("Year"),
            "imdb_id": data.get("imdbID"),
            "box_office": data.get("BoxOffice")
        }

    except requests.RequestException as error:
        print(f"API request failed for {title}: {error}")
        raise





def extract_release_year(title):
    """Extract the release year from a MovieLens title."""

    match =re.search(r"\((\d{4})\)\s*$", title)

    if match:
        return int(match.group(1))

    return None


def clean_box_office(value):
    """Convert an OMDb box office value into an integer."""

    if not value or value == "N/A":
        return None

    cleaned_value = value.replace("$", "").replace(",", "").strip()

    try:
        return int(cleaned_value)
    except ValueError:
        return None

def parse_genres(genres):
    """Split a pipe-separated genre string into a list."""

    if not genres or genres == "(no genres listed)":
        return []

    return [
        genre.strip()
        for genre in genres.split("|")
        if genre.strip()
    ]

def transform_movie_row(movie):
    """Transform one MovieLens movie row."""

    title = movie["title"]
    genres = parse_genres(movie["genres"])
    release_year = extract_release_year(title)

    return {
        "movie_id": int(movie["movieId"]),
        "title": title,
        "release_year": release_year,
        "genres": genres
    }

def transform_movie_with_details(movie, details):
    """Combine MovieLens data with OMDb details."""

    movie_data = transform_movie_row(movie)

    if details:
        movie_data["director"] = details.get("director")
        movie_data["plot"] = details.get("plot")
        movie_data["imdb_id"] = details.get("imdb_id")

        # Prefer the release year from the MovieLens title.
        movie_data["release_year"] = (
            movie_data["release_year"]
            or extract_release_year(details.get("release_year", ""))
        )

        movie_data["box_office"] = clean_box_office(
            details.get("box_office")
        )
    else:
        movie_data.update({
            "director": None,
            "plot": None,
            "imdb_id": None,
            "box_office": None
        })

    return movie_data



def load_movie(connection, movie):
    """Insert or update a movie and its genres."""

    connection.execute("""
        INSERT INTO movies (
            movie_id, title, release_year,
            director, plot, box_office, imdb_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(movie_id) DO UPDATE SET
            title = excluded.title,
            release_year = excluded.release_year,
            director = excluded.director,
            plot = excluded.plot,
            box_office = excluded.box_office,
            imdb_id = excluded.imdb_id
    """, (
        movie["movie_id"],
        movie["title"],
        movie["release_year"],
        movie.get("director"),
        movie.get("plot"),
        movie.get("box_office"),
        movie.get("imdb_id")
    ))

    for genre in movie["genres"]:
        connection.execute("""
            INSERT INTO genres (genre_name)
            VALUES (?)
            ON CONFLICT(genre_name) DO NOTHING
        """, (genre,))

        genre_id = connection.execute("""
            SELECT genre_id
            FROM genres
            WHERE genre_name = ?
        """, (genre,)).fetchone()[0]

        connection.execute("""
            INSERT INTO movie_genres (movie_id, genre_id)
            VALUES (?, ?)
            ON CONFLICT(movie_id, genre_id) DO NOTHING
        """, (movie["movie_id"], genre_id))

def load_all_movies_without_api(connection, movies):
    """Load all MovieLens movies and genres before ratings."""

    for _, row in movies.iterrows():
        movie = transform_movie_row(row)

        connection.execute("""
            INSERT INTO movies (movie_id, title, release_year)
            VALUES (?, ?, ?)
            ON CONFLICT(movie_id) DO UPDATE SET
                title = excluded.title,
                release_year = excluded.release_year
        """, (
            movie["movie_id"],
            movie["title"],
            movie["release_year"]
        ))

        for genre in movie["genres"]:
            connection.execute("""
                INSERT INTO genres (genre_name)
                VALUES (?)
                ON CONFLICT(genre_name) DO NOTHING
            """, (genre,))

            genre_id = connection.execute("""
                SELECT genre_id FROM genres WHERE genre_name = ?
            """, (genre,)).fetchone()[0]

            connection.execute("""
                INSERT INTO movie_genres (movie_id, genre_id)
                VALUES (?, ?)
                ON CONFLICT(movie_id, genre_id) DO NOTHING
            """, (movie["movie_id"], genre_id))

    connection.commit()
    print(f"Loaded {len(movies)} movies and their genres.")


def load_ratings(connection, ratings):
    """Insert ratings without creating duplicates."""

    rows = [
        (
            int(row.userId),
            int(row.movieId),
            float(row.rating),
            int(row.timestamp)
        )
        for row in ratings.itertuples(index=False)
    ]

    connection.executemany("""
        INSERT INTO ratings (user_id, movie_id, rating, timestamp)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, movie_id) DO UPDATE SET
            rating = excluded.rating,
            timestamp = excluded.timestamp
    """, rows)

    print(f"Ratings loaded: {len(rows)}")


import json




def enrich_movies(connection, movies, batch_size=5):
    """Fetch and cache OMDb details for a small batch of movies."""

    if not os.getenv("OMDB_API_KEY"):
        raise RuntimeError("OMDB_API_KEY is not set.")

    # Find movies that have not been attempted yet.
    pending = connection.execute("""
        SELECT m.movie_id, m.title, m.release_year
        FROM movies AS m
        LEFT JOIN omdb_cache AS c
            ON m.movie_id = c.movie_id
        WHERE c.movie_id IS NULL
        ORDER BY m.movie_id
        LIMIT ?
    """, (batch_size,)).fetchall()

    for movie_id, title, year in pending:
        # Remove the trailing year, e.g. "(1995)".
        search_title = re.sub(r"\s*\(\d{4}\)\s*$", "", title)

        try:
            details = fetch_movie_details(search_title, year)

        except RuntimeError as error:
            # API-level errors must stop the batch.
            connection.rollback()
            raise RuntimeError(
                f"Stopping enrichment because of an OMDb API error for "
                f"{title}: {error}"
            ) from error

        except requests.RequestException as error:
            # Leave network failures uncached so they can be retried.
            print(f"Temporary network error for {title}: {error}")
            continue

        if details is None:
            status = "not_found"
            response_json = None

        else:
            status = "success"
            response_json = json.dumps(details)

            connection.execute("""
                UPDATE movies
                SET director = ?,
                    plot = ?,
                    imdb_id = ?,
                    box_office = ?
                WHERE movie_id = ?
            """, (
                details.get("director"),
                details.get("plot"),
                details.get("imdb_id"),
                clean_box_office(details.get("box_office")),
                movie_id
            ))

        connection.execute("""
            INSERT INTO omdb_cache (movie_id, response_json, status)
            VALUES (?, ?, ?)
        """, (movie_id, response_json, status))

        connection.commit()
        print(f"Processed {movie_id}: {title} [{status}]")

    print(f"Batch complete: {len(pending)} movies selected.")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the movie data ETL pipeline."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of movies to enrich per run (default: 5)."
    )
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")

    movies, ratings = extract_csv_data()
    connection = sqlite3.connect("movies.db")

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        load_all_movies_without_api(connection, movies)
        load_ratings(connection, ratings)
        connection.commit()

        enrich_movies(
            connection,
            movies,
            batch_size=args.batch_size
        )
    finally:
        connection.close()








