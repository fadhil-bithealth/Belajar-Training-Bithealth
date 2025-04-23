import typesense
from pprint import pprint

client = typesense.Client({
  'api_key': 'xyz123',
  'nodes': [{
    'host': 'localhost',
    'port': '8108',
    'protocol': 'http'
  }],
  'connection_timeout_seconds': 2
})

def search_products(query, filter_category=None, max_price=None):
    search_params = {
        'q': query,
        'query_by': 'name,description',
        'per_page': 10
    }
    
    # Tambahkan filter jika ada
    filters = []
    if filter_category:
        filters.append(f"category:={filter_category}")
    if max_price:
        filters.append(f"price:<={max_price}")
    
    if filters:
        search_params['filter_by'] = ' && '.join(filters)
    
    return client.collections['products'].documents.search(search_params)

if __name__ == '__main__':
    print("=== Typesense Product Search ===")
    while True:
        query = input("\nSearch query (atau 'exit' untuk keluar): ").strip()
        if query.lower() == 'exit':
            break
            
        category = input("Filter kategori (kosongkan jika tidak ada): ").strip() or None
        max_price = input("Harga maksimal (kosongkan jika tidak ada): ").strip() or None
        
        try:
            results = search_products(
                query,
                filter_category=category,
                max_price=float(max_price) if max_price else None
            )
            
            print(f"\nFound {results['found']} products:")
            for hit in results['hits']:
                doc = hit['document']
                print(f"\n- {doc['name']} (${doc['price']})")
                print(f"  {doc['description']}")
                print(f"  Category: {doc['category']} (Relevance score: {hit['text_match']})")
                
        except Exception as e:
            print(f"Error: {str(e)}")