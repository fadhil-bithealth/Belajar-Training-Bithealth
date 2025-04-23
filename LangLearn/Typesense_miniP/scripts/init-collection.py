import json
import typesense

client = typesense.Client({
  'api_key': 'xyz123',
  'nodes': [{
    'host': 'localhost',
    'port': '8108',
    'protocol': 'http'
  }],
  'connection_timeout_seconds': 2
})

# Buat schema koleksi
try:
    client.collections.create({
        "name": "products",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "price", "type": "float"},
            {"name": "category", "type": "string", "facet": True}
        ],
        "default_sorting_field": "price"
    })
except typesense.exceptions.ObjectAlreadyExists:
    print("Koleksi sudah ada, melanjutkan...")

# Import data produk
from pathlib import Path
import json

file_path = Path(__file__).resolve().parent.parent / "data" / "products.json"
with open(file_path) as f:
    products = json.load(f)

for product in products:
    try:
        client.collections['products'].documents.create(product)
        print(f"Produk {product['name']} berhasil ditambahkan")
    except typesense.exceptions.ObjectAlreadyExists:
        print(f"Produk {product['name']} sudah ada")