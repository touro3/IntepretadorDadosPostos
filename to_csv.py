import pandas as pd

# Read TSV file
df = pd.read_csv("2004-2021.tsv", sep="\t")

# Save as CSV
df.to_csv("data.csv", index=False)
