import pandas as pd

def load_sales_data(path):
    return pd.read_csv(
        path,
        delimiter="|",
        encoding="latin1",
        engine="python"
    )
