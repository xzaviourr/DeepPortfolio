import pandas as pd
from typing import List

from src.models.holding import Holding

def load_holdings(file_path: str) -> List[Holding]:
    actual_holdings = pd.read_csv(file_path)
    holdings = []
    for _, row in actual_holdings.iterrows():
        holdings.append(Holding(
            symbol = row['Instrument'],
            quantity = row['Qty.'],
            buy_average = row['Avg. cost']
        ))
    return holdings
