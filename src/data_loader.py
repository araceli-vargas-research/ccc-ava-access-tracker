from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_csv(relative_path: str) -> pd.DataFrame:
    path = DATA_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path)
