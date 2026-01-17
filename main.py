from utils.file_handler import read_sales_data
from utils.data_processor import parse_transactions, validate_and_filter, calculate_total_revenue
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data

def main():
    print("=== Q4: API ENRICHMENT ===")
    
    # Load sales data
    raw_lines = read_sales_data('data/sales_data.txt')
    all_transactions = parse_transactions(raw_lines)
    valid_transactions, invalid_count, summary = validate_and_filter(all_transactions)

    print(f"📊 Loaded {len(valid_transactions)} valid transactions")
    
    # Show first transaction structure (DEBUG)
    if valid_transactions:
        print(f"First transaction type: {type(valid_transactions[0])}")
        print(f"First transaction keys: {valid_transactions[0].keys() if isinstance(valid_transactions[0], dict) else 'NOT DICT'}")
    
    # Fetch API products
    api_products = fetch_all_products()
    product_mapping = create_product_mapping(api_products)
    
    # Enrich data
    enriched_data = enrich_sales_data(valid_transactions, product_mapping)
    
    print("✅ Q4 COMPLETE - Check data/enriched_sales_data.txt")

if __name__ == "__main__":
    main()
