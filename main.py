from utils.file_handler import read_sales_data
from utils.data_processor import parse_transactions, validate_and_filter
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data
from utils.report_generator import generate_sales_report

def main():
    print("=== Q5: FULL SALES ANALYTICS SYSTEM ===")
    
    # Load and process sales data
    raw_lines = read_sales_data('data/sales_data.txt')
    all_transactions = parse_transactions(raw_lines)
    valid_transactions, invalid_count, summary = validate_and_filter(all_transactions)
    
    # API Enrichment
    api_products = fetch_all_products()
    product_mapping = create_product_mapping(api_products)
    enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)
    
    # Generate Report
    generate_sales_report(valid_transactions, enriched_transactions)
    
    print("🎉 FULL ASSIGNMENT COMPLETE!")
    print("📄 Check output/sales_report.txt for complete analysis")

if __name__ == "__main__":
    main()
