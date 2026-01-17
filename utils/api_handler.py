import requests
import json
import os
import re

def fetch_all_products():
    """Fetches products from API or local file"""
    try:
        # Try API first
        url = 'https://dummyjson.com/products?limit=100'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Fetched {len(data['products'])} products from API")
        return data['products']
    except:
        # Fallback to local file
        try:
            with open('data/products.json', 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded {len(data['products'])} products from file")
                return data['products']
        except Exception as e:
            print(f"❌ No products: {e}")
            return []

def create_product_mapping(api_products):
    """ID → product info mapping"""
    mapping = {}
    for p in api_products:
        mapping[p['id']] = {
            'title': p['title'],
            'category': p['category'],
            'brand': p.get('brand', 'Unknown'),
            'rating': p['rating']
        }
    print(f"✅ Created mapping for {len(mapping)} products")
    return mapping

def extract_product_id(product_id_str):
    """Extract numeric ID from ProductID like 'P101' → 101"""
    # Handle dict/list input - get string value first
    if isinstance(product_id_str, (dict, list)):
        product_id_str = str(product_id_str).split('ProductID')[-1].split('P')[-1][:3]
    
    if not isinstance(product_id_str, str):
        product_id_str = str(product_id_str)
    
    import re
    match = re.search(r'P(\d+)', product_id_str)
    return int(match.group(1)) if match else None

def enrich_sales_data(transactions, product_mapping):
    """Enrich transactions - handles ALL data types bulletproof"""
    enriched = []
    
    for item in transactions:
        # Handle ANY input type
        t_dict = {}
        
        # Case 1: Already dict
        if isinstance(item, dict):
            t_dict = item.copy()
        # Case 2: List with expected fields  
        elif isinstance(item, list) and len(item) >= 8:
            field_order = ['TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 
                          'UnitPrice', 'CustomerID', 'Region']
            t_dict = dict(zip(field_order, item[:8]))
        # Case 3: Skip invalid
        else:
            continue
        
        # Extract ProductID safely
        prod_id_str = str(t_dict.get('ProductID', ''))
        prod_id = None
        if 'P' in prod_id_str:
            try:
                # Extract number after P (P101 → 101)
                num_str = ''.join(filter(str.isdigit, prod_id_str))
                prod_id = int(num_str[:3]) if num_str else None
            except:
                prod_id = None
        
        # Enrich with API data
        if prod_id and prod_id in product_mapping:
            api_data = product_mapping[prod_id]
            t_dict.update({
                'API_Category': api_data.get('category'),
                'API_Brand': api_data.get('brand', 'Unknown'),
                'API_Rating': api_data.get('rating'),
                'API_Match': True
            })
        else:
            t_dict.update({
                'API_Category': None,
                'API_Brand': None,
                'API_Rating': None,
                'API_Match': False
            })
        
        enriched.append(t_dict)
    
    print(f"✅ Enriched {len(enriched)} transactions (input had {len(transactions)} items)")
    save_enriched_data(enriched)
    return enriched



def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """Save enriched data to pipe-delimited file"""
    if not enriched_transactions:
        print("❌ No data to save")
        return
    
    # Header
    header = ['TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 
              'UnitPrice', 'CustomerID', 'Region', 'API_Category', 
              'API_Brand', 'API_Rating', 'API_Match']
    
    with open(filename, 'w') as f:
        f.write('|'.join(header) + '\n')
        
        for t in enriched_transactions:
            row = []
            for field in header:
                value = t.get(field, '')
                if value is None:
                    value = ''
                row.append(str(value))
            f.write('|'.join(row) + '\n')
    
    print(f"✅ Saved enriched data to {filename}")
