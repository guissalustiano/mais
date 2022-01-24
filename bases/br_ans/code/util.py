import pandas as pd
from pathlib import Path

datapath = Path('../output')

def load_df(df: pd.DataFrame, path: str):
    final_path = (datapath / path).with_suffix('.csv')
    final_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(final_path)
