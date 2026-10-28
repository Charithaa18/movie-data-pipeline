
import unittest
from unittest.mock import Mock, patch

import requests

from etl import fetch_movie_details


class TestFetchMovieDetails(unittest.TestCase):

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key(self):
        with self.assertRaisesRegex(RuntimeError, "OMDB_API_KEY"):
            fetch_movie_details("Toy Story", 1995)

    @patch("etl.requests.get")
    @patch.dict("os.environ", {"OMDB_API_KEY": "test-key"})
    def test_successful_response(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "Response": "True",
            "Director": "John Lasseter",
            "Plot": "A cowboy doll...",
            "Year": "1995",
            "imdbID": "tt0114709",
            "BoxOffice": "$191,796,233"
        }
        mock_get.return_value = mock_response

        result = fetch_movie_details("Toy Story", 1995)

        self.assertEqual(result["director"], "John Lasseter")
        self.assertEqual(result["imdb_id"], "tt0114709")
        mock_get.assert_called_once()

    @patch("etl.requests.get")
    @patch.dict("os.environ", {"OMDB_API_KEY": "test-key"})
    def test_movie_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "Response": "False",
            "Error": "Movie not found!"
        }
        mock_get.return_value = mock_response

        result = fetch_movie_details("Nonexistent Movie")

        self.assertIsNone(result)

    @patch("etl.requests.get")
    @patch.dict("os.environ", {"OMDB_API_KEY": "test-key"})
    def test_invalid_api_key(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "Response": "False",
            "Error": "Invalid API key!"
        }
        mock_get.return_value = mock_response

        with self.assertRaisesRegex(RuntimeError, "rejected the API key"):
            fetch_movie_details("Toy Story")

    @patch("etl.requests.get")
    @patch.dict("os.environ", {"OMDB_API_KEY": "test-key"})
    def test_network_failure(self, mock_get):
        mock_get.side_effect = requests.Timeout("Request timed out")

        with self.assertRaises(requests.Timeout):
            fetch_movie_details("Toy Story")


if __name__ == "__main__":
    unittest.main(verbosity=2)

