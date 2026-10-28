
import pandas as pd

# Read the two CSV files
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# Display the first 5 rows
print("MOVIES DATA")
print(movies.head())

print("\nRATINGS DATA")
print(ratings.head())

# Display the number of rows and columns
print("\nMovies shape:", movies.shape)
print("Ratings shape:", ratings.shape)

# Display the column names
print("\nMovies columns:", movies.columns.tolist())
print("Ratings columns:", ratings.columns.tolist())


print("\nMOVIES DATA TYPES")
print(movies.dtypes)

print("\nRATINGS DATA TYPES")
print(ratings.dtypes)

print("\nMISSING VALUES IN MOVIES")
print(movies.isnull().sum())

print("\nMISSING VALUES IN RATINGS")
print(ratings.isnull().sum())
