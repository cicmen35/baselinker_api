import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_URL = "https://api.baselinker.com/connector.php"

# Get TOKEN from environment variables, with a fallback default value
TOKEN = os.getenv("TOKEN", "your_token_here")

INVENTORY_ID = 833
TARGET_PRODUCT_ID = "12064368"
EXTRA_FIELD_1_ID = "extra_field_483"
EXTRA_FIELD_2_ID = "extra_field_484"