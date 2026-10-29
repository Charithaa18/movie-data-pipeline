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
- `unittest` for automated testing

## 3. Data Sources

### MovieLens

The `ml-latest-small` dataset provides two input files:

- `movies.csv`: Movie IDs, titles, and genres.
- `ratings.csv`: User IDs, movie IDs, ratings, and timestamps.

Download the dataset from [MovieLens](https://grouplens.org/datasets/movielens/latest/).

### OMDb API

The OMDb API provides additional movie information, including director, plot, release year, IMDb ID, and box office earnings when available.

OMDb metadata is optional and may be unavailable for some MovieLens titles.

## 4. Database Design

The database contains five tables:

- **movies:** Stores movie titles, release years, directors, plots, box office earnings, and IMDb IDs.
- **genres:** Stores unique genre names.
- **movie_genres:** Maps movies to their genres using a many-to-many relationship.
- **ratings:** Stores user ratings and timestamps.
- **omdb_cache:** Tracks OMDb lookup outcomes to avoid repeating completed requests.

Primary keys, foreign keys, unique constraints, and rating checks help maintain data integrity.

SQLite was selected because it is lightweight, requires no separate database server, and is suitable for this dataset.

## 5. ETL Workflow

1. **Extract:** Read `movies.csv` and `ratings.csv` using Pandas.
2. **Transform:** Extract release years from movie titles, split pipe-separated genres, clean box office values, and prepare movie records.
3. **Load:** Store movies, genres, genre relationships, and ratings in SQLite.
4. **Enrich:** Fetch additional movie details from OMDb in configurable batches.
5. **Cache:** Record successful and not-found lookup results so completed lookups can be skipped in subsequent runs.

The loading logic uses conflict-handling SQL statements to avoid duplicate records when the pipeline is rerun.

## 6. Setup Instructions

### Prerequisites

Install Python 3.11 or a compatible version.

Download the MovieLens `ml-latest-small` dataset and place `movies.csv` and `ratings.csv` in the project directory.

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure the OMDb API key

Obtain an API key from [OMDb API](https://www.omdbapi.com/apikey.aspx).

In **Git Bash**, set the key for the current terminal session:

```bash
export OMDB_API_KEY="your_api_key_here"
```

In **Windows Command Prompt**, use:

```bat
set OMDB_API_KEY=your_api_key_here
```

Replace the placeholder with your own key. Never commit a real API key to version control.

### Initialize the database

Run:

```bash
python test_schema.py
```

This script creates the database tables using `schema.sql`. Run it before the first ETL execution on a fresh setup.

### Run the ETL pipeline

```bash
python etl.py
```

The default batch size is five uncached movies. To select a different batch size, use:

```bash
python etl.py --batch-size 20
```

Only use a batch size appropriate for your available API quota. Successful and not-found lookups are cached; network failures can be retried in later runs.

## 7. SQL Analytical Queries

The `queries.sql` file contains queries to answer these questions:

1. Which movie has the highest average rating?
2. Which five genres have the highest average rating?
3. Which director has the most movies?
4. What is the average rating for each release year?

Run the query tests with:

```bash
python test_queries.py
```

Interpret the results in light of the metadata available in the database. In particular, the director analysis depends on successful OMDb enrichment.

## 8. Testing and Data Quality

Run the following commands from the project directory:

```bash
python test_schema.py
python test_api.py
python test_queries.py
python data_quality.py
python verify_database.py
```

The API tests use mocks to test API behavior without making live OMDb requests.

The data-quality script checks for missing identifiers and titles, invalid movie and genre references, and foreign-key violations.

## 9. Validation Results

The initial MovieLens load was verified to contain:

- 9,742 movies
- 100,836 ratings
- 19 distinct genres
- 22,050 movie-genre relationships

In the latest validation run, the database contained 687 cached OMDb lookup outcomes: 450 successful lookups and 237 movies not found by OMDb.

 HEAD
These results represent partial enrichment, not complete OMDb coverage. The full MovieLens dataset is loaded, but director, plot, IMDb ID, and box office information may be unavailable for many movies. Director-related analysis should therefore be interpreted based on the metadata available..

These results represent partial enrichment, not complete OMDb coverage. The full MovieLens dataset is loaded, but director, plot, IMDb ID, and box office information may be unavailable for many movies. Director-related analysis should therefore be interpreted based on the metadata available.
4d1649b (update enrichment validation results)

## 10. Challenges and Design Decisions

### Movie title mismatches

Some MovieLens titles do not match OMDb titles exactly. The pipeline removes the year suffix before searching. More advanced title normalization and alternative-title matching are potential improvements.

### API limits and repeated requests

The pipeline processes small batches and caches lookup outcomes to reduce repeated requests and support resumable execution.

### Data integrity

Primary keys, foreign keys, rating constraints, and conflict-handling SQL statements help maintain database consistency.

### Missing metadata

Some OMDb fields may be unavailable. Optional metadata is stored as `NULL` rather than assuming every movie has complete information.

### Error handling

The API integration checks for missing API keys, unsuccessful lookups, invalid responses, and request failures. Network failures are left uncached so that they can be retried.

## 11. Future Improvements

- Improve title matching with normalized and alternative titles.
- Add retry policies with backoff and request throttling.
- Distinguish temporary API failures from permanent not-found results.
- Improve test coverage for malformed responses and HTTP failures.
- Consider PostgreSQL for larger workloads requiring concurrent access.
- Schedule incremental updates and monitor data quality.

## 12. Project Files

- `etl.py`: ETL pipeline and OMDb enrichment.
- `schema.sql`: Database table definitions.
- `queries.sql`: Analytical SQL queries.
- `test_schema.py`: Database schema validation and setup.
- `test_api.py`: Mocked API unit tests.
- `test_queries.py`: SQL query tests.
- `data_quality.py`: Data-quality checks.
- `verify_database.py`: Database row-count verification.
- `requirements.txt`: Python dependencies.
- `README.md`: Project documentation.
