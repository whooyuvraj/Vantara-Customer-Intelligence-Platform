import os
import zipfile
import urllib.request
import pandas as pd

url = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
zip_path = "online_retail_ii.zip"
extracted_folder = "extracted_data"

print("Downloading zip archive from UCI...")
urllib.request.urlretrieve(url, zip_path)

print("Extracting zip archive...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extracted_folder)

# Locate extracted Excel file
excel_path = os.path.join(extracted_folder, "online_retail_II.xlsx")

print("Loading sheets into Pandas (this may take 20-30 seconds)...")
df_1 = pd.read_excel(excel_path, sheet_name="Year 2009-2010")
df_2 = pd.read_excel(excel_path, sheet_name="Year 2010-2011")

print("Combining sheets...")
df = pd.concat([df_1, df_2], ignore_index=True)

# Ensure raw data folder exists
os.makedirs("data/raw", exist_ok=True)

print("\nDataset loaded successfully!")
print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

# Save combined dataset locally as CSV
df.to_csv("data/raw/online_retail_II.csv", index=False)
print("\nSaved raw data to data/raw/online_retail_II.csv")

# Cleanup temporary download files
if os.path.exists(zip_path):
    os.remove(zip_path)
