from typing import Hashable


import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
postgres_url: str | None = os.getenv("DATABASE_URL")

df = pd.read_csv("./data/male_players.csv")
df.drop(list[Hashable](df.columns[:2]), axis=1, inplace=True)

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

engine = create_engine(postgres_url)

df.to_sql("players", engine, if_exists="replace", index=False)

print("✅ Data loaded into PostgreSQL successfully.")
