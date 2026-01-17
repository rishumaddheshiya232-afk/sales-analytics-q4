from utils.data_processor import calculate_total_revenue, region_wise_sales, top_selling_products, customer_analysis, daily_sales_trend, find_peak_sales_day, low_performing_products
from datetime import datetime
import os

def format_currency(amount):
    """Format number with commas: 1545000 → 1,545,000"""
    return f"₹{amount:,.2f}"

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """Generates comprehensive formatted text report"""
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 1. HEADER
        f.write("=" * 55 + "\n")
        f.write("           SALES ANALYTICS REPORT\n")
        f.write(f"         Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"         Records Processed: {len(transactions)}\n")
        f.write("=" * 55 + "\n\n")
        
        # 2. OVERALL SUMMARY
        f.write("OVERALL SUMMARY\n")
        f.write("-" * 55 + "\n")
        total_revenue = calculate_total_revenue(transactions)
        f.write(f"Total Revenue:        {format_currency(total_revenue)}\n")
        f.write(f"Total Transactions:   {len(transactions)}\n")
        avg_order = total_revenue / len(transactions) if transactions else 0
        f.write(f"Average Order Value:  {format_currency(avg_order)}\n")
        
        dates = [t['Date'] for t in transactions]
        date_range = f"{min(dates)} to {max(dates)}" if dates else "No data"
        f.write(f"Date Range:           {date_range}\n\n")
        
        # 3. REGION-WISE PERFORMANCE
        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Region':<12} {'Sales':<12} {'% of Total':<12} {'Transactions':<12}\n")
        f.write("-" * 55 + "\n")
        
        regions = region_wise_sales(transactions)
        for region, data in regions.items():
            pct = data['percentage']
            f.write(f"{region:<12} {format_currency(data['total_sales']):<12} "
                   f"{pct:<12.1f}% {data['transaction_count']:<12}\n")
        f.write("\n")
        
        # 4. TOP 5 PRODUCTS
        f.write("TOP 5 PRODUCTS\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Rank':<5} {'Product Name':<20} {'Qty Sold':<10} {'Revenue':<15}\n")
        f.write("-" * 55 + "\n")
        
        top_products = top_selling_products(transactions, n=5)
        for i, (name, qty, revenue) in enumerate(top_products, 1):
            f.write(f"{i:<5} {name:<20.19} {qty:<10} {format_currency(revenue):<15}\n")
        f.write("\n")
        
        # 5. TOP 5 CUSTOMERS
        f.write("TOP 5 CUSTOMERS\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Rank':<5} {'Customer ID':<12} {'Total Spent':<15} {'Order Count':<12}\n")
        f.write("-" * 55 + "\n")
        
        customers = customer_analysis(transactions)
        top_customers = list(customers.items())[:5]
        for i, (cust_id, data) in enumerate(top_customers, 1):
            f.write(f"{i:<5} {cust_id:<12} {format_currency(data['total_spent']):<15} "
                   f"{data['purchase_count']:<12}\n")
        f.write("\n")
        
        # 6. DAILY SALES TREND
        f.write("DAILY SALES TREND\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Date':<12} {'Revenue':<15} {'Transactions':<12} {'Unique Cust':<12}\n")
        f.write("-" * 55 + "\n")
        
        daily = daily_sales_trend(transactions)
        for date, data in sorted(daily.items()):
            f.write(f"{date:<12} {format_currency(data['revenue']):<15} "
                   f"{data['transaction_count']:<12} {data['unique_customers']:<12}\n")
        f.write("\n")
        
        # 7. PRODUCT PERFORMANCE ANALYSIS
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("-" * 55 + "\n")
        peak_day = find_peak_sales_day(transactions)
        f.write(f"Best Selling Day: {peak_day[0]} (₹{peak_day[1]:,.2f}, {peak_day[2]} transactions)\n\n")
        
        low_products = low_performing_products(transactions, threshold=10)
        if low_products:
            f.write("Low Performing Products (<10 units):\n")
            for name, qty, revenue in low_products:
                f.write(f"  {name}: {qty} units, ₹{revenue:,.2f}\n")
        else:
            f.write("No low performing products\n")
        f.write("\n")
        
        # 8. API ENRICHMENT SUMMARY
        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-" * 55 + "\n")
        enriched_count = sum(1 for t in enriched_transactions if t.get('API_Match', False))
        success_rate = (enriched_count / len(enriched_transactions)) * 100 if enriched_transactions else 0
        f.write(f"Products Enriched:    {enriched_count}/{len(enriched_transactions)}\n")
        f.write(f"Success Rate:         {success_rate:.1f}%\n")
        
        unmatched = [t['ProductID'] for t in enriched_transactions if not t.get('API_Match', False)]
        if unmatched:
            f.write(f"Unmatched Products:   {', '.join(set(unmatched[:10]))}{'...' if len(unmatched) > 10 else ''}\n")
        f.write("\n")
        
        f.write("END OF REPORT\n")
        f.write("=" * 55 + "\n")
    
    print(f"✅ Report generated: {output_file}")
