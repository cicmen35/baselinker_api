# Baselinker API Application

This application interacts with the Baselinker API to:
1. List all products in inventory ID 833
2. Display product details (id, sku, ean, name, field1, field2)
3. Allow updating the second extra field (extra_field_484) for product ID 12064368

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the command-line script:
   ```
   python main.py
   ```

3. Or run the Streamlit web interface:
   ```
   streamlit run app.py
   ```

## Features

### Command-line Interface
The main.py script will:
1. Connect to Baselinker API using the provided token
2. Fetch all products from inventory 833
3. Display them in a table format
4. Prompt you to enter a new value for Field 2 (extra_field_484) for product ID 12064368
5. Update the product with the new value

### Streamlit Web Interface
The app.py Streamlit application provides a user-friendly web interface with:
1. A product list view showing all products in the inventory
2. An update form to change the value of Field 2 for the target product
3. Immediate feedback on the success or failure of update operations

## API Methods Used

- getInventoryProductsList - To get all products in the inventory
- getInventoryProductsData - To get detailed information about the products
- addInventoryProduct - To update the product's extra field

## Project Structure

- baselinker_api.py - Core functions for interacting with the Baselinker API
- main.py - Command-line interface
- app.py - Streamlit web interface
- requirements.txt - Project dependencies
