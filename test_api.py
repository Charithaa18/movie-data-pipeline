
import os
import requests

# Get the API key from the environment variable
api_key = os.getenv("OMDB_API_KEY")

# Search for one movie
url = "https://www.omdbapi.com/"
params = {
    "apikey": api_key,
    "t": "Toy Story",
    "y": 1995
}

response = requests.get(url, params=params, timeout=15)

# Convert the response to JSON
data = response.json()

# Display the result
print("API response:", data.get("Response"))
print("Movie title:", data.get("Title"))
print("Director:", data.get("Director"))
print("Release year:", data.get("Year"))
print("Genre:", data.get("Genre"))
print("Plot:", data.get("Plot"))
