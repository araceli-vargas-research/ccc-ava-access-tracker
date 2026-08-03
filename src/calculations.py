import pandas as pd

def rate_per_million(events: pd.Series, miles: pd.Series) -> pd.Series:
    return (events / miles) * 1_000_000
