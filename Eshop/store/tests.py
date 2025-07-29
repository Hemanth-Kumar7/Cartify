import requests
import json

data = requests.get("https://fakestoreapi.com/products").json()

with open("products.json", "w") as f:
    json.dump(data, f)

