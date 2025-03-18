import streamlit as st
import pandas as pd
import json
from baselinker_api import (
    get_inventory_products_list,
    get_inventory_products_data,
    update_product_extra_field,
    INVENTORY_ID,
    TARGET_PRODUCT_ID,
    EXTRA_FIELD_1_ID,
    EXTRA_FIELD_2_ID
)

st.set_page_config(page_title="Baselinker Products")
products_list = get_inventory_products_list(INVENTORY_ID)

if "status" in products_list and products_list["status"] == "SUCCESS":
    product_ids = []
    if "products" in products_list:
        if isinstance(products_list["products"], list):
            product_ids = [product["id"] for product in products_list["products"]]
        elif isinstance(products_list["products"], dict):
            product_ids = list(products_list["products"].keys())
    
    if not product_ids and TARGET_PRODUCT_ID:
        product_ids = [TARGET_PRODUCT_ID]

    products_data = get_inventory_products_data(INVENTORY_ID, product_ids)
    
    if "status" in products_data and products_data["status"] == "SUCCESS":
        # Prepare data for display
        table_data = []
        for product_id, product in products_data["products"].items():
            # Flatten the product data for tabular display
            product_info = {
                "ID": product_id,
                "SKU": product.get("sku", ""),
                "EAN": product.get("ean", ""),
                "Name": product.get("text_fields", {}).get("name", ""),
                "Extra Field 467": product.get("text_fields", {}).get("extra_field_467", ""),
                "Extra Field 484": product.get("text_fields", {}).get("extra_field_484", ""),
                "Description Extra 1": product.get("text_fields", {}).get("description_extra1", ""),
                "Description Extra 2": product.get("text_fields", {}).get("description_extra2", "")
            }
            table_data.append(product_info)
        
        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Display products table
        st.header("Products in Inventory")
        st.dataframe(df, use_container_width=True)
        
        # File uploader
        uploaded_file = st.file_uploader("Upload CSV or XLS file", type=["csv", "xls", "xlsx"])

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    uploaded_data = pd.read_csv(uploaded_file)
                else:
                    uploaded_data = pd.read_excel(uploaded_file)
                
                st.write("Uploaded Data:")
                st.dataframe(uploaded_data)
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Update section
        st.header(f"Update Extra Field 484 for Product ID: {TARGET_PRODUCT_ID}")
        
        # Get current value for the target product
        current_value = ""
        target_row = df[df["ID"] == TARGET_PRODUCT_ID]
        if "Extra Field 484" in target_row.columns:
            current_value = target_row.iloc[0]["Extra Field 484"]
        else:
            current_value = "N/A"
        st.write(f"Current value: {current_value}")
        
        # Input for new value
        new_value = st.text_input("Enter new value for Extra Field 484:")
        
        # Update button
        if st.button("Update Extra Field 484"):
            if new_value:
                update_result = update_product_extra_field(
                    INVENTORY_ID, 
                    TARGET_PRODUCT_ID, 
                    EXTRA_FIELD_2_ID, 
                    new_value
                )
                
                if "status" in update_result and update_result["status"] == "SUCCESS":
                    st.success(f"Successfully updated product ID {TARGET_PRODUCT_ID} with new Extra Field 484 value: {new_value}")
                    st.info("Refresh the page to see the updated value.")
                else:
                    st.error(f"Failed to update product: {update_result}")
            else:
                st.warning("Please enter a value to update.")
    else:
        st.error(f"Failed to get product data: {products_data}")
else:
    st.error(f"Failed to get products list: {products_list}")
