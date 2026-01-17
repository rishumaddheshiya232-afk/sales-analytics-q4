from utils.file_handler import read_sales_data
from utils.data_processor import (parse_transactions, validate_and_filter, 
                                 calculate_total_revenue, region_wise_sales, 
                                 top_selling_products, customer_analysis, 
                                 daily_sales_trend, find_peak_sales_day, 
                                 low_performing_products)
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data
from utils.report_generator import generate_sales_report
import sys

def print_step(step_num, step_desc, status=""):
    """Print formatted step progress"""
    print(f"\n[{step_num}/13] {step_desc}...", end=" ")
    if status:
        print(f"✓ {status}")
    else:
        sys.stdout.flush()

def get_user_filter(transactions):
    """Interactive filter selection"""
    print_step("", "Filter Options Available:")
    
    # Show regions
    regions = list(set(t['Region'] for t in transactions if t.get('Region')))
    regions = [r for r in regions if r]  # Remove empty
    print(f"   Regions: {', '.join(regions)}")
    
    # Show amount range
    amounts = [t['Quantity'] * t['UnitPrice'] for t in transactions]
    print(f"   Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}")
    
    choice = input("\nDo you want to filter data? (y/n): ").lower().strip()
    if choice != 'y':
        return transactions
    
    # Get filter criteria
    region_filter = input("Enter region to filter (or Enter for none): ").strip()
    min_amount = input("Enter minimum amount (or Enter for none): ").strip()
    max_amount = input("Enter maximum amount (or Enter for none): ").strip()
    
    min_amt_val = float(min_amount) if min_amount else None
    max_amt_val = float(max_amount) if max_amount else None
    
    filtered, invalid, summary = validate_and_filter(
        transactions, 
        region=region_filter if region_filter else None,
        min_amount=min_amt_val,
        max_amount=max_amt_val
    )
    print(f"   Filtered to {len(filtered)} records")
    return filtered

def main():
    try:
        print("=" * 47)
        print("      SALES ANALYTICS SYSTEM")
        print("=" * 47)
        
        # 1. Read sales data
        print_step(1, "Reading sales data...")
        raw_lines = read_sales_data('data/sales_data.txt')
        print_step(1, "Reading sales data...", f"✓ Successfully read {len(raw_lines)} transactions")
        
        # 2. Parse data
        print_step(2, "Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print_step(2, "Parsing and cleaning data...", f"✓ Parsed {len(transactions)} records")
        
        # 3. Filter options
        filtered_transactions = get_user_filter(transactions)
        
        # 4. Validate
        print_step(4, "Validating transactions...")
        valid_transactions, invalid_count, summary = validate_and_filter(filtered_transactions)
        print_step(4, "Validating transactions...", f"✓ Valid: {len(valid_transactions)} | Invalid: {invalid_count}")
        
        # 5. Analyze
        print_step(5, "Analyzing sales data...")
        _ = calculate_total_revenue(valid_transactions)  # Trigger all analyses
        _ = region_wise_sales(valid_transactions)
        _ = top_selling_products(valid_transactions)
        _ = customer_analysis(valid_transactions)
        _ = daily_sales_trend(valid_transactions)
        _ = find_peak_sales_day(valid_transactions)
        _ = low_performing_products(valid_transactions)
        print_step(5, "Analyzing sales data...", "✓ Analysis complete")
        
        # 6. API
        print_step(6, "Fetching product data from API...")
        api_products = fetch_all_products()
        product_mapping = create_product_mapping(api_products)
        print_step(6, "Fetching product data from API...", f"✓ Fetched {len(api_products)} products")
        
        # 7. Enrich
        print_step(7, "Enriching sales data...")
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)
        enriched_count = sum(1 for t in enriched_transactions if t.get('API_Match', False))
        success_rate = (enriched_count / len(enriched_transactions)) * 100 if enriched_transactions else 0
        print_step(7, "Enriching sales data...", f"✓ Enriched {enriched_count}/{len(enriched_transactions)} ({success_rate:.1f}%)")
        
        # 8. Save enriched
        print_step(8, "Saving enriched data...")
        # Already saved in enrich_sales_data
        print_step(8, "Saving enriched data...", "✓ Saved to: data/enriched_sales_data.txt")
        
        # 9. Generate report
        print_step(9, "Generating report...")
        generate_sales_report(valid_transactions, enriched_transactions)
        print_step(9, "Generating report...", "✓ Report saved to: output/sales_report.txt")
        
        # 10. Complete
        print_step(10, "Process Complete!")
        print("=" * 47)
        
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {str(e)}")
        print("Please check your data files and try again.")

if __name__ == "__main__":
    main()
