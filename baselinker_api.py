import requests
import json
from tabulate import tabulate
import dotenv

dotenv.load_dotenv()


API_URL = "https://api.baselinker.com/connector.php"
TOKEN = dotenv.dotenv_values(".env")["TOKEN"]
INVENTORY_ID = 833
TARGET_PRODUCT_ID = "12064368"
EXTRA_FIELD_1_ID = "extra_field_483"
EXTRA_FIELD_2_ID = "extra_field_484"


def make_request(method, parameters=None):
    """Make a request to the Baselinker api"""
    if parameters is None:
        parameters = {}
        
    data = {
        "token": TOKEN,
        "method": method,
        "parameters": json.dumps(parameters)
    }
    
    response = requests.post(API_URL, data=data)
    return response.json()

def get_inventories():
    """Get all inventories"""
    return make_request("getInventories")

def get_inventory_products_list(inventory_id):
    """Get list of products in an inventory"""
    parameters = {"inventory_id": inventory_id}
    return make_request("getInventoryProductsList", parameters)

def get_inventory_products_data(inventory_id, products):
    """Get detailed data for products in an inventory"""
    parameters = {
        "inventory_id": inventory_id,
        "products": products
    }
    return make_request("getInventoryProductsData", parameters)

def update_product_extra_field(inventory_id, product_id, field_id, value):
    """Update a product's extra field in text_fields"""
    parameters = {
        "inventory_id": inventory_id,
        "product_id": product_id,
        "text_fields": {
            field_id: value
        }
    }
    return make_request("addInventoryProduct", parameters)

