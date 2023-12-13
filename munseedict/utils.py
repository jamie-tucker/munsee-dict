import pandas as pd
from pathlib import Path

def get_csv(filename):
  mod_path = Path(__file__).parent
  filepath = (mod_path / "../data/input/" / filename).resolve()
  return pd.read_csv(filepath)