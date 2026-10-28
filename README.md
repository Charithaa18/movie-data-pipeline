# Building a Simple Movie Data Pipeline

## 1. Project Overview

This project implements an ETL (Extract, Transform, Load) pipeline using Python to process movie and rating data from the MovieLens dataset, enrich movie information using the OMDb API, and store the data in a relational SQLite database.

The pipeline supports analytical SQL queries to explore movie ratings, genres, directors, and release-year trends.

## 2. Technologies Used

- Python 3.11
- Pandas for CSV processing
- Requests for API calls
- SQLite for relational data storage
- SQL for data analysis
- OMDb API for movie metadata enrichment

## 3. Data Sources

### MovieLens

The `ml-latest-small` dataset provides two input files:

- `movies.csv`: Movie IDs, titles, and genres.
- `ratings.csv`: User IDs, movie IDs, ratings, and timestamps.

### OMDb API

The OMDb API provides additional movie information, including director, plot, release year, IMDb ID, and box office earnings when available.

## 4. Database Design

The database contains five tables:

- **movies:** Stores movie titles, release years, directors, plots, box office earnings, and IMDb IDs.
- **genres:** Stores unique genre names.
- **movie_genres:** Maps movies to their genres using a many-to-many relationship.
- **ratings:** Stores user ratings and timestamps.
- **omdb_cache:** Tracks OMDb lookup results to avoid repeatedly requesting movies already processed.

Primary keys, foreign keys, unique constraints, and rating checks help maintain data integrity.

SQLite was selected because it is lightweight, free, and suitable for this small dataset.

## 5. ETL Workflow

1. **Extract:** Read `movies.csv` and `ratings.csv` using Pandas.
2. **Transform:** Extract release years from movie titles, split pipe-separated genres, clean box office values, and combine movie data with API responses.
3. **Load:** Store movies, genres, genre relationships, and ratings in SQLite.
4. **Enrich:** Fetch additional movie details from OMDb in small batches.
5. **Cache:** Record successful and not-found lookup results so previously attempted movies can be skipped in subsequent runs.

The database loading logic uses conflict handling to make repeated executions safe against duplicate records.

## 6. Setup Instructions

### Prerequisites

Install Python 3.11 or a compatible Python version.

Download the MovieLens `ml-latest-small` dataset from:

https://grouplens.org/datasets/movielens/latest/

Place `movies.csv` and `ratings.csv` in the project directory.

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure the OMDb API key

Obtain a free API key from:

https://www.omdbapi.com/apikey.aspx

In Windows Command Prompt, set the key for your current terminal session:

```bat
set OMDB_API_KEY=your_api_key_here
```

Replace the placeholder with your own key. Never commit your real API key to version control.

### Create the database schema

```bash
python test_schema.py
```

### Run the ETL pipeline

```bash
python etl.py
```

The current script processes five uncached movies per run. Running it again continues with additional movies, subject to API limits.

## 7. Running the SQL Queries

The `queries.sql` file contains queries to answer these questions:

1. Which movie has the highest average rating?
2. Which five genres have the highest average rating?
3. Which director has the most movies?
4. What is the average rating for each release year?

Execute and test the queries with:

```bash
python test_queries.py
```

## 8. Validation

Run the database verification script:

```bash
python verify_database.py
```

The initial database load was verified to contain:

- 9,742 movies
- 100,836 ratings
- 19 distinct genres
- 22,050 movie-genre relationships

OMDb enrichment is currently partial, so director-related analysis should be interpreted accordingly until more metadata has been processed.

## 9. Challenges and Solutions

### Movie title mismatches

Some MovieLens titles do not match OMDb titles exactly. The pipeline removes the year suffix before searching and handles not-found responses without stopping the entire batch.

### API limits and repeated requests

The pipeline processes small batches and caches lookup outcomes to reduce repeated API calls and support resumable execution.

### Data integrity

Primary keys, foreign keys, and conflict-handling SQL statements help prevent duplicate records and maintain relationships between movies, genres, and ratings.

### Missing metadata

Some OMDb fields may be unavailable. The pipeline allows optional metadata to remain empty rather than assuming every movie has complete information.

## 10. Future Improvements

- Improve title matching using IMDb IDs or alternative-title searches.
- Add configurable batch sizes, retries with backoff, and request throttling.
- Add structured logging and more automated tests.
- Track failed API requests separately from genuine not-found results.
- Use PostgreSQL for a larger, concurrent production workload.
- Schedule incremental data updates and monitor data quality.

## 11. Project Files

- `etl.py`: Extraction, transformation, loading, and metadata enrichment.
- `schema.sql`: Database table definitions.
- `queries.sql`: Analytical SQL queries.
- `README.md`: Project overview and execution instructions.
