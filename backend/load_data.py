import pandas as pd
from sqlalchemy import create_engine, text

USERNAME = "myuser"
PASSWORD = "mypassword"
DB_HOSTNAME = "localhost"
DB_NAME = "fc25"
DATABASE_URI = f"postgresql://{USERNAME}:{PASSWORD}@{DB_HOSTNAME}/{DB_NAME}"

df = pd.read_csv("./data/male_players.csv")
df.drop(list(df.columns[:2]), axis=1, inplace=True)

df.fillna(
    value={
        'Alternative positions': 'Unknown',
        'play style': 'Unknown',
        'GK Diving': 0,
        'GK Handling': 0,
        'GK Kicking': 0,
        'GK Positioning': 0,
        'GK Reflexes': 0,
    },
    inplace=True
)

df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

engine = create_engine(DATABASE_URI)

df.to_sql("players", engine, if_exists="replace", index=False)

print("✅ Data loaded into PostgreSQL successfully.")
