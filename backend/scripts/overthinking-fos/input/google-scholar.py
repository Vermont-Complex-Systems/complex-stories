import pandas as pd
import sys

def scrape_googlescholar():
    # Define field categories and their URLs
    fields = {
        'Business Economics Management': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=bus',
        'Chemistry Material Science': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=chm',
        'Engineering Computer Science': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=eng',
        'Health Medicine': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=med',
        'Humanities Literature Arts': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=hum',
        'Life Earth Sciences': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=bio',
        'Physics Mathematics': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=phy',
        'Social Sciences': 'https://scholar.google.com/citations?view_op=top_venues&hl=en&vq=soc'
    }

    # Scrape data from each field
    field_dataframes = []
    field_stats = {}
    for field_name, url in fields.items():
        try:
            df_list = pd.read_html(url)
            df = df_list[0]  # Take the first table
            df['field'] = field_name  # Add field identifier
            field_dataframes.append(df)
            field_stats[field_name] = len(df)
        except Exception as e:
            print(f"Error scraping {field_name}: {e}")
            print(f"URL: {url}")
            field_stats[field_name] = 0

    # Combine all fields
    if field_dataframes:
        combined_data = pd.concat(field_dataframes, axis=0, ignore_index=True)
        
        # Create simple schema
        df_simple = pd.DataFrame({
            'source': 'gscholar_venues',
            'venue': combined_data.Publication,  # First column is typically the venue name
            'field': combined_data.field,
            'h5_index': combined_data['h5-index'],
            'h5_median': combined_data['h5-median']
        })
    
        df_simple.to_parquet("input/google-scholar.parquet")

def main():
    """Main scraping function - downloads PDF only."""
    try:
        scrape_googlescholar()
        return True

    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)