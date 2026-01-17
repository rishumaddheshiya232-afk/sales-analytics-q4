def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues
    Returns: list of raw lines (strings) - skips header & empty lines
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                lines = f.readlines()
                # Skip header (first line) and empty lines
                raw_lines = [line.strip() for line in lines[1:] if line.strip()]
                print(f"Successfully read with encoding: {encoding}")
                return raw_lines
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"ERROR: File '{filename}' not found!")
            return []
    
    print("ERROR: Could not read file with any encoding!")
    return []
