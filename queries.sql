

-- 1. Highest average-rated movie with at least 20 ratings
SELECT
    m.movie_id,
    m.title,
    ROUND(AVG(r.rating), 2) AS average_rating,
    COUNT(r.rating) AS total_ratings
FROM movies AS m
JOIN ratings AS r
    ON m.movie_id = r.movie_id
GROUP BY m.movie_id, m.title
HAVING COUNT(r.rating) >= 20
ORDER BY AVG(r.rating) DESC, total_ratings DESC
LIMIT 1;



-- 2. Top 5 genres with the highest average rating
SELECT
    g.genre_name,
    ROUND(AVG(r.rating), 2) AS average_rating,
    COUNT(r.rating) AS total_ratings
FROM genres AS g
JOIN movie_genres AS mg
    ON g.genre_id = mg.genre_id
JOIN ratings AS r
    ON mg.movie_id = r.movie_id
GROUP BY g.genre_name
ORDER BY average_rating DESC, total_ratings DESC
LIMIT 5;


-- 3. Director with the most movies
-- Split comma-separated director names and count each director separately.
WITH RECURSIVE director_split(movie_id, director, remaining) AS (
    SELECT
        movie_id,
        '',
        director || ','
    FROM movies
    WHERE director IS NOT NULL
      AND TRIM(director) != ''
      AND director != 'N/A'

    UNION ALL

    SELECT
        movie_id,
        TRIM(SUBSTR(remaining, 1, INSTR(remaining, ',') - 1)),
        SUBSTR(remaining, INSTR(remaining, ',') + 1)
    FROM director_split
    WHERE remaining != ''
)
SELECT
    director,
    COUNT(DISTINCT movie_id) AS total_movies
FROM director_split
WHERE director != ''
  AND director != 'N/A'
GROUP BY director
ORDER BY total_movies DESC, director ASC
LIMIT 1;


-- 4. Average rating of movies released each year
SELECT
    m.release_year,
    ROUND(AVG(r.rating), 2) AS average_rating,
    COUNT(r.rating) AS total_ratings
FROM movies AS m
JOIN ratings AS r
    ON m.movie_id = r.movie_id
WHERE m.release_year IS NOT NULL
GROUP BY m.release_year
ORDER BY m.release_year ASC;
