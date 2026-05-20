import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOP_URL = os.environ.get("SHOPIFY_STORE_URL", "https://agentlens-ai.myshopify.com")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = "2026-04"

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def get_products():
    url = f"{SHOP_URL}/admin/api/{API_VERSION}/products.json"
    response = requests.get(url, headers=headers)
    return response.json().get("products", [])

def get_policies():
    url = f"{SHOP_URL}/admin/api/{API_VERSION}/policies.json"
    response = requests.get(url, headers=headers)
    return response.json().get("policies", [])

def update_product(product_id, update_data):
    url = f"{SHOP_URL}/admin/api/{API_VERSION}/products/{product_id}.json"
    payload = {"product": update_data}
    response = requests.put(url, headers=headers, json=payload)
    return response.json().get("product")