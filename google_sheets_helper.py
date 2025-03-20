import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pandas as pd
import json
from settings import EXTRA_FIELD_2_ID
import pickle

# Define the scope
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheets_client():
    """
    Authenticate and create a Google Sheets client using OAuth2
    
    Returns:
        gspread.Client: Authenticated Google Sheets client
    """
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    
    # Check if token.pickle exists (saved credentials)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            try:
                creds = pickle.load(token)
            except Exception:
                # If token file is corrupted, we'll create a new one
                creds = None
    
    # If no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if credentials file exists
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    "credentials.json file not found. Please place your Google API credentials file in the project directory."
                )
            
            # Load client secrets from credentials.json
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
    
    # Return the authenticated client
    return gspread.authorize(creds)

def get_sheet_data(spreadsheet_url, worksheet_name=0):
    """
    Get data from a Google Sheet
    
    Args:
        spreadsheet_url (str): URL or key of the spreadsheet
        worksheet_name (str or int, optional): Name or index of the worksheet. Defaults to 0 (first sheet).
    
    Returns:
        pandas.DataFrame: DataFrame containing the sheet data
    """
    client = get_google_sheets_client()
    
    # Open the spreadsheet
    try:
        spreadsheet = client.open_by_url(spreadsheet_url) if 'http' in spreadsheet_url else client.open_by_key(spreadsheet_url)
    except gspread.exceptions.SpreadsheetNotFound:
        raise ValueError(f"Spreadsheet not found: {spreadsheet_url}")
    
    # Get the worksheet
    if isinstance(worksheet_name, int):
        worksheet = spreadsheet.get_worksheet(worksheet_name)
    else:
        worksheet = spreadsheet.worksheet(worksheet_name)
    
    if not worksheet:
        raise ValueError(f"Worksheet not found: {worksheet_name}")
    
    # Get all values
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def update_sheet_with_product_data(spreadsheet_url, product_data, worksheet_name=0):
    """
    Update a Google Sheet with product data
    
    Args:
        spreadsheet_url (str): URL or key of the spreadsheet
        product_data (dict): Dictionary containing product data
        worksheet_name (str or int, optional): Name or index of the worksheet. Defaults to 0 (first sheet).
    
    Returns:
        bool: True if update was successful
    """
    client = get_google_sheets_client()
    
    # Open the spreadsheet
    try:
        spreadsheet = client.open_by_url(spreadsheet_url) if 'http' in spreadsheet_url else client.open_by_key(spreadsheet_url)
    except gspread.exceptions.SpreadsheetNotFound:
        raise ValueError(f"Spreadsheet not found: {spreadsheet_url}")
    
    # Get the worksheet
    if isinstance(worksheet_name, int):
        worksheet = spreadsheet.get_worksheet(worksheet_name)
    else:
        worksheet = spreadsheet.worksheet(worksheet_name)
    
    if not worksheet:
        raise ValueError(f"Worksheet not found: {worksheet_name}")
    
    # Update the worksheet with the product data
    # Assuming the first row contains headers
    headers = worksheet.row_values(1)
    
    # Find the product ID column and the Extra Field 484 column
    id_col = None
    extra_field_col = None
    
    for i, header in enumerate(headers):
        if header.lower() == "id":
            id_col = i + 1  # 1-indexed
        elif header.lower() == "extra field 484":
            extra_field_col = i + 1  # 1-indexed
    
    if id_col is None or extra_field_col is None:
        raise ValueError("Required columns 'ID' and 'Extra Field 484' not found in the sheet")
    
    # Find the row with the matching product ID
    cell_list = worksheet.findall(product_data["ID"])
    product_row = None
    
    for cell in cell_list:
        if cell.col == id_col:
            product_row = cell.row
            break
    
    if product_row is None:
        # Product not found, add a new row
        new_row = [""] * len(headers)
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if header_lower == "id":
                new_row[i] = product_data["ID"]
            elif header_lower == "extra field 484":
                new_row[i] = product_data.get("Extra Field 484", "")
            elif header_lower in [k.lower() for k in product_data.keys()]:
                # Find the case-insensitive match
                for k in product_data.keys():
                    if k.lower() == header_lower:
                        new_row[i] = product_data[k]
                        break
        
        worksheet.append_row(new_row)
    else:
        # Update the existing row
        worksheet.update_cell(product_row, extra_field_col, product_data.get("Extra Field 484", ""))
    
    return True

def get_products_from_sheet(spreadsheet_url, worksheet_name=0):
    """
    Get product data from a Google Sheet
    
    Args:
        spreadsheet_url (str): URL or key of the spreadsheet
        worksheet_name (str or int, optional): Name or index of the worksheet. Defaults to 0 (first sheet).
    
    Returns:
        pandas.DataFrame: DataFrame containing the product data
    """
    df = get_sheet_data(spreadsheet_url, worksheet_name)
    
    # Ensure required columns exist
    required_columns = ["ID", "Extra Field 484"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Required columns missing from sheet: {', '.join(missing_columns)}")
    
    return df

def update_product_from_sheet(spreadsheet_url, product_id, update_func, worksheet_name=0):
    """
    Update a product's extra_field_484 value from Google Sheets
    
    Args:
        spreadsheet_url (str): URL or key of the spreadsheet
        product_id (str): ID of the product to update
        update_func (callable): Function to call to update the product
        worksheet_name (str or int, optional): Name or index of the worksheet. Defaults to 0 (first sheet).
    
    Returns:
        dict: Result of the update operation
    """
    df = get_products_from_sheet(spreadsheet_url, worksheet_name)
    
    # Find the product in the sheet
    product_row = df[df["ID"] == product_id]
    
    if product_row.empty:
        return {"status": "ERROR", "error": f"Product ID {product_id} not found in the sheet"}
    
    # Get the extra_field_484 value
    extra_field_value = product_row.iloc[0]["Extra Field 484"]
    
    # Update the product
    inventory_id = product_row.iloc[0].get("Inventory ID", None)
    if not inventory_id:
        from settings import INVENTORY_ID
        inventory_id = INVENTORY_ID
    
    result = update_func(
        inventory_id,
        product_id,
        EXTRA_FIELD_2_ID,
        extra_field_value
    )
    
    return result
