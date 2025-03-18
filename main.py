#!/usr/bin/env python3
from baselinker_api import *

if __name__ == "__main__":
    products_list = get_inventory_products_list(INVENTORY_ID)
    print("API Response Structure:")
    print(json.dumps(products_list, indent=2))
    
    if "status" in products_list and products_list["status"] == "SUCCESS":
        product_ids = []
        if "products" in products_list:
            if isinstance(products_list["products"], list):
                product_ids = [product["id"] for product in products_list["products"]]
            elif isinstance(products_list["products"], dict):
                product_ids = list(products_list["products"].keys())
    
        print(f"Found {len(product_ids)} products")

        if not product_ids and TARGET_PRODUCT_ID:
            product_ids = [TARGET_PRODUCT_ID]
            print(f"Using test product ID: {TARGET_PRODUCT_ID}")

        products_data = get_inventory_products_data(INVENTORY_ID, product_ids)
        print("\nProduct Data Structure:")
        print(json.dumps(products_data, indent=2))
        
        if "status" in products_data and products_data["status"] == "SUCCESS":
            table_data = []
            for product_id, product in products_data["products"].items():
                extra_field_1 = product.get("text_fields", {}).get(EXTRA_FIELD_1_ID, "")
                extra_field_2 = product.get("text_fields", {}).get(EXTRA_FIELD_2_ID, "")
                
                table_data.append([
                    product_id,
                    product.get("sku", ""),
                    product.get("ean", ""),
                    product.get("name", ""),
                    extra_field_1,
                    extra_field_2
                ])
            
            headers = ["ID", "SKU", "EAN", "Name", "Field 1", "Field 2"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print(f"\nUpdate {EXTRA_FIELD_2_ID} for product ID {TARGET_PRODUCT_ID}:")
            new_value = input("Enter new value for Field 2: ")
            update_result = update_product_extra_field(INVENTORY_ID, TARGET_PRODUCT_ID, EXTRA_FIELD_2_ID, new_value)
            
            if "status" in update_result and update_result["status"] == "SUCCESS":
                print(f"Successfully updated product ID {TARGET_PRODUCT_ID} with new Field 2 value: {new_value}")
            else:
                print(f"Failed to update product: {update_result}")
        else:
            print(f"Failed to get product data: {products_data}")
    else:
        print(f"Failed to get products list: {products_list}")
