import pandas as pd

# Replace 'your_file.csv' with the path to your downloaded CSV file
df = pd.read_csv('global_mean_sea_level_1993-2024.csv')

# Show the first few rows of the dataset
print(df.head())
