import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

file_list = [
    "Album.csv", "Artist.csv", "Customer.csv", "Employee.csv", 
    "Genre.csv", "Invoice.csv", "InvoiceLine.csv", "MediaType.csv", 
    "Playlist.csv", "PlaylistTrack.csv", "Track.csv"
]

# PostgreSQL connection string
engine = create_engine(
    "postgresql://postgres:VtpkeZFGdLVgaAryorLqIiIxSHqqkyNv@gondola.proxy.rlwy.net:12215/railway"
)


for file in file_list:
    try:
        temp_df = pd.read_csv(BASE_DIR / file)
        
        table_name = file.split('.')[0]
        
        temp_df.to_sql(table_name, engine, if_exists="replace", index=False)
        
        print(f"Successfully uploaded {file} to table '{table_name}'")
        
    except Exception as e:
        print(f"Error uploading {file}: {e}")


print("\n--- Verifying table 'Artist' ---")
with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT * FROM \"Artist\" LIMIT 5;"))
        for row in result:
            print(row)
    except Exception as e:
        print(f"Could not verify: {e}")