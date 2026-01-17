import re

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    Handles commas in ProductName and numbers
    """
    transactions = []
    
    for line in raw_lines:
        # Split by pipe |
        fields = line.split('|')
        if len(fields) < 8:  # Skip incorrect fields
            continue
            
        # Clean fields
        trans_id = fields[0].strip()
        date = fields[1].strip()
        prod_id = fields[2].strip()
        prod_name = re.sub(r',', ' ', fields[3].strip())  # "Mouse, Wireless" → "Mouse Wireless"
        qty_str = re.sub(r',', '', fields[4].strip())    # "1,500" → "1500"
        unit_str = re.sub(r',', '', fields[5].strip())
        cust_id = fields[6].strip()
        region = fields[7].strip()
        
        # Convert numbers
        try:
            quantity = int(qty_str)
            unit_price = float(unit_str)
        except:
            continue  # Skip invalid numbers
            
        transaction = {
            'TransactionID': trans_id,
            'Date': date,
            'ProductID': prod_id,
            'ProductName': prod_name,
            'Quantity': quantity,  # int
            'UnitPrice': unit_price,  # float
            'CustomerID': cust_id,
            'Region': region
        }
        transactions.append(transaction)
    
    return transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    Returns: (valid_transactions, invalid_count, filter_summary)
    """
    valid_transactions = []
    invalid_count = 0
    
    # Print available regions
    regions = set(t['Region'] for t in transactions)
    print("Available regions:", ', '.join(regions))
    
    # Print amount range
    amounts = [t['Quantity'] * t['UnitPrice'] for t in transactions]
    print(f"Transaction amount range: {min(amounts):.2f} - {max(amounts):.2f}")
    
    for t in transactions:
        amount = t['Quantity'] * t['UnitPrice']
        
        # VALIDATION - skip invalid
        if (t['Quantity'] <= 0 or t['UnitPrice'] <= 0 or
            not t['TransactionID'].startswith('T') or
            not t['ProductID'].startswith('P') or
            not t['CustomerID'].startswith('C') or
            not t['Region']):
            invalid_count += 1
            continue
        
        # FILTERS
        if region and t['Region'] != region:
            continue
        if min_amount and amount < min_amount:
            continue
        if max_amount and amount > max_amount:
            continue
            
        valid_transactions.append(t)
    
    # Summary
    filter_summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': len(transactions) - len(valid_transactions) if region else 0,
        'filtered_by_amount': 0,  # Simplified
        'final_count': len(valid_transactions)
    }
    
    print(f"After validation: {len(valid_transactions)} valid, {invalid_count} invalid")
    return valid_transactions, invalid_count, filter_summary

# ============= TASK 2.1 =============
def calculate_total_revenue(transactions):
    """Calculates total revenue from all transactions"""
    total = sum(t['Quantity'] * t['UnitPrice'] for t in transactions)
    return round(total, 2)

def region_wise_sales(transactions):
    """Analyzes sales by region - sorted by total sales DESC"""
    regions = {}
    
    for t in transactions:
        region = t['Region']
        if region not in regions:
            regions[region] = {'total_sales': 0.0, 'transaction_count': 0}
        regions[region]['total_sales'] += t['Quantity'] * t['UnitPrice']
        regions[region]['transaction_count'] += 1
    
    # Calculate percentages and sort
    total_sales = calculate_total_revenue(transactions)
    for region in regions:
        regions[region]['percentage'] = round(
            (regions[region]['total_sales'] / total_sales) * 100, 2
        )
    
    # Sort by total_sales DESC
    return dict(sorted(regions.items(), key=lambda x: x[1]['total_sales'], reverse=True))

def top_selling_products(transactions, n=5):
    """Top n products by total quantity sold"""
    products = {}
    
    for t in transactions:
        name = t['ProductName']
        qty = t['Quantity']
        revenue = qty * t['UnitPrice']
        
        if name not in products:
            products[name] = {'total_qty': 0, 'total_revenue': 0.0}
        products[name]['total_qty'] += qty
        products[name]['total_revenue'] += revenue
    
    # Convert to list of tuples, sort by qty DESC
    product_list = [(name, data['total_qty'], round(data['total_revenue'], 2)) 
                   for name, data in products.items()]
    return sorted(product_list, key=lambda x: x[1], reverse=True)[:n]

def customer_analysis(transactions):
    """Customer purchase patterns - sorted by total_spent DESC"""
    customers = {}
    
    for t in transactions:
        cust = t['CustomerID']
        amount = t['Quantity'] * t['UnitPrice']
        
        if cust not in customers:
            customers[cust] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }
        customers[cust]['total_spent'] += amount
        customers[cust]['purchase_count'] += 1
        customers[cust]['products_bought'].add(t['ProductName'])
    
    # Convert sets to lists and calculate avg
    for cust in customers:
        customers[cust]['avg_order_value'] = round(
            customers[cust]['total_spent'] / customers[cust]['purchase_count'], 2
        )
        customers[cust]['products_bought'] = list(customers[cust]['products_bought'])
    
    # Sort by total_spent DESC
    return dict(sorted(customers.items(), key=lambda x: x[1]['total_spent'], reverse=True))

# ============= TASK 2.2 =============
def daily_sales_trend(transactions):
    """Daily sales trends - chronological order"""
    daily = {}
    
    for t in transactions:
        date = t['Date']
        amount = t['Quantity'] * t['UnitPrice']
        
        if date not in daily:
            daily[date] = {'revenue': 0.0, 'transaction_count': 0, 'unique_customers': set()}
        daily[date]['revenue'] += amount
        daily[date]['transaction_count'] += 1
        daily[date]['unique_customers'].add(t['CustomerID'])
    
    # Convert sets to counts
    for date in daily:
        daily[date]['unique_customers'] = len(daily[date]['unique_customers'])
        daily[date]['revenue'] = round(daily[date]['revenue'], 2)
    
    # Sort chronologically
    return dict(sorted(daily.items()))

def find_peak_sales_day(transactions):
    """Find date with highest revenue"""
    daily = daily_sales_trend(transactions)
    peak_date = max(daily.items(), key=lambda x: x[1]['revenue'])
    date, data = peak_date
    return (date, data['revenue'], data['transaction_count'])

# ============= TASK 2.3 =============
def low_performing_products(transactions, threshold=10):
    """Products with total quantity < threshold - sorted ASC"""
    products = {}
    
    for t in transactions:
        name = t['ProductName']
        qty = t['Quantity']
        revenue = qty * t['UnitPrice']
        
        if name not in products:
            products[name] = {'total_qty': 0, 'total_revenue': 0.0}
        products[name]['total_qty'] += qty
        products[name]['total_revenue'] += revenue
    
    # Filter low performers and sort ASC by quantity
    low_performers = [(name, data['total_qty'], round(data['total_revenue'], 2))
                     for name, data in products.items() if data['total_qty'] < threshold]
    return sorted(low_performers, key=lambda x: x[1])
