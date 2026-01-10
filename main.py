import pandas as pd
from utils.file_handler import load_sales_data
from utils.data_processor import clean_and_validate
from utils.api_handler import enrich_products

def main():
    df = load_sales_data("data/sales_data.txt")
    cleaned_records = clean_and_validate(df)
    enriched = enrich_products(cleaned_records)

    final_df = pd.DataFrame(enriched)
    final_df["TotalAmount"] = final_df["Quantity"] * final_df["UnitPrice"]

    final_df.to_csv("output/cleaned_sales_data.csv", index=False)

if __name__ == "__main__":
    main()
