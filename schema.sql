
-- Store one record per movie
CREATE TABLE IF NOT EXISTS movies (
    movie_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    release_year INTEGER,
    director TEXT,
    plot TEXT,
    box_office INTEGER,
    imdb_id TEXT
);



-- Store each unique genre once
CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY,
    genre_name TEXT NOT NULL UNIQUE
);

-- Connect movies to their genres
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,

    PRIMARY KEY (movie_id, genre_id),

    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);


-- Store individual user ratings
CREATE TABLE IF NOT EXISTS ratings (
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    timestamp INTEGER NOT NULL,

    PRIMARY KEY (user_id, movie_id),

    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),

    CHECK (rating >= 0.5 AND rating <= 5.0)
);

--This table will record whether each movie was successfully enriched or wasn't found, so we can skip completed requests on later runs.
CREATE TABLE IF NOT EXISTS omdb_cache (
    movie_id INTEGER PRIMARY KEY,
    response_json TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);