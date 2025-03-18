import requests
import json
from tabulate import tabulate
import gspread


API_URL = "https://api.baselinker.com/connector.php"
TOKEN = "6000739-6000727-7C9O730TUE77SJ795CG9UP4H6HWHAGH3X2MY2CDVA0V41T7U39EPYSFUV52PHLWB"
INVENTORY_ID = 833
TARGET_PRODUCT_ID = "12064368"
EXTRA_FIELD_1_ID = "extra_field_483"
EXTRA_FIELD_2_ID = "extra_field_484"


# Google Sheets API setup
credentials = {
    "installed": {
        "client_id": "12345678901234567890abcdefghijklmn.apps.googleusercontent.com",
        "project_id": "my-project1234",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "MySecRet....",
        "redirect_uris": ["http://localhost"]
    }
}
authorized_user = {
    "refresh_token": "8//ThisALONGTOkEn....",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "12345678901234567890abcdefghijklmn.apps.googleusercontent.com",
    "client_secret": "MySecRet....",
    "scopes": [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ],
    "expiry": "1070-01-01T00:00:00.000001Z"
}

gc, authorized_user = gspread.oauth_from_dict(credentials, authorized_user)

# Access the spreadsheet
sh = gc.open("Example spreadsheet")

# Example: Read a cell value
cell_value = sh.sheet1.get('A1')
print(f"Value in A1: {cell_value}")


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
