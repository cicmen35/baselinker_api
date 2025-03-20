import streamlit as st
import pandas as pd
import json
import os
from baselinker_api import (
    get_inventory_products_list,
    get_inventory_products_data,
    update_product_extra_field,
    INVENTORY_ID,
    TARGET_PRODUCT_ID,
    EXTRA_FIELD_1_ID,
    EXTRA_FIELD_2_ID
)
from google_sheets_helper import (
    get_products_from_sheet,
    update_product_from_sheet,
    update_sheet_with_product_data
)

st.set_page_config(page_title="Baselinker Products", layout="wide")

# Initialize session state variables
if 'products_data' not in st.session_state:
    st.session_state.products_data = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'spreadsheet_url' not in st.session_state:
    st.session_state.spreadsheet_url = ""

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Baselinker Products", "Google Sheets Integration"])

# Function to load products data
def load_products_data():
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
            st.session_state.products_data = products_data
            prepare_dataframe()
            return True
        else:
            st.error(f"Failed to get product data: {products_data}")
            return False
    else:
        st.error(f"Failed to get products list: {products_list}")
        return False

# Function to prepare DataFrame
def prepare_dataframe():
    if st.session_state.products_data is None:
        return
    
    table_data = []
    for product_id, product in st.session_state.products_data["products"].items():
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
    st.session_state.df = pd.DataFrame(table_data)

# Load products data if not already loaded
if st.session_state.products_data is None:
    load_products_data()

# Baselinker Products Page
if page == "Baselinker Products":
    if st.session_state.df is not None:
        # Display products table
        st.header("Products in Inventory")
        st.dataframe(st.session_state.df, use_container_width=True)
        
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
        target_row = st.session_state.df[st.session_state.df["ID"] == TARGET_PRODUCT_ID]
        if not target_row.empty and "Extra Field 484" in target_row.columns:
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
                    
                    # Reload products data
                    load_products_data()
                else:
                    st.error(f"Failed to update product: {update_result}")
            else:
                st.warning("Please enter a value to update.")
    else:
        st.info("Loading products data...")
        load_products_data()

# Google Sheets Integration Page
elif page == "Google Sheets Integration":
    st.header("Google Sheets Integration")
    
    # Check for credentials file
    creds_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if not os.path.exists(creds_file):
        st.error(
            "Google Sheets credentials file not found. Please upload your credentials.json file to the project directory."
        )
        
        # Instructions for getting credentials
        with st.expander("How to get Google Sheets credentials"):
            st.markdown("""
            1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select an existing one
            3. Enable the Google Sheets API and Google Drive API
            4. Go to the Credentials page and create OAuth client ID credentials
            5. Select "Desktop app" as the application type
            6. Download the OAuth client ID credentials as JSON
            7. Rename the downloaded file to `credentials.json` and place it in the project directory
            8. When you first use the Google Sheets integration, you'll be prompted to authorize the application
            """)
    else:
        # Google Sheets URL input
        spreadsheet_url = st.text_input(
            "Enter Google Sheets URL or ID", 
            value=st.session_state.spreadsheet_url,
            help="Enter the full URL of your Google Sheet or just the spreadsheet ID"
        )
        st.session_state.spreadsheet_url = spreadsheet_url
        
        # Worksheet selection
        worksheet_name = st.text_input(
            "Worksheet Name (leave blank for first sheet)", 
            help="Enter the name of the worksheet or leave blank to use the first sheet"
        )
        
        worksheet = 0 if not worksheet_name else worksheet_name
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Button to load data from Google Sheets
            if st.button("Load Data from Google Sheets"):
                if spreadsheet_url:
                    try:
                        sheet_df = get_products_from_sheet(spreadsheet_url, worksheet)
                        st.success("Successfully loaded data from Google Sheets")
                        st.dataframe(sheet_df)
                        
                        # Option to update Baselinker from Google Sheets
                        st.subheader("Update Baselinker from Google Sheets")
                        
                        if "ID" in sheet_df.columns and "Extra Field 484" in sheet_df.columns:
                            product_id = st.selectbox(
                                "Select Product ID to update", 
                                sheet_df["ID"].tolist(),
                                index=0 if TARGET_PRODUCT_ID in sheet_df["ID"].tolist() else None
                            )
                            
                            if st.button("Update Product from Google Sheets"):
                                result = update_product_from_sheet(
                                    spreadsheet_url, 
                                    product_id,
                                    update_product_extra_field,
                                    worksheet
                                )
                                
                                if "status" in result and result["status"] == "SUCCESS":
                                    st.success(f"Successfully updated product ID {product_id} from Google Sheets")
                                    # Reload products data
                                    load_products_data()
                                else:
                                    st.error(f"Failed to update product: {result}")
                        else:
                            st.warning("The Google Sheet must contain 'ID' and 'Extra Field 484' columns")
                    except Exception as e:
                        st.error(f"Error loading data from Google Sheets: {str(e)}")
                else:
                    st.warning("Please enter a Google Sheets URL or ID")
        
        with col2:
            # Button to export data to Google Sheets
            if st.button("Export Baselinker Data to Google Sheets"):
                if spreadsheet_url and st.session_state.df is not None:
                    try:
                        for _, row in st.session_state.df.iterrows():
                            product_data = row.to_dict()
                            update_sheet_with_product_data(spreadsheet_url, product_data, worksheet)
                        
                        st.success("Successfully exported data to Google Sheets")
                    except Exception as e:
                        st.error(f"Error exporting data to Google Sheets: {str(e)}")
                elif not spreadsheet_url:
                    st.warning("Please enter a Google Sheets URL or ID")
                else:
                    st.warning("No product data available to export")
                    if st.button("Load Baselinker Products"):
                        load_products_data()
