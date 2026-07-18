"""
Configuration for Clean Stream Pro Wash Meta Ads Management
All secrets come from environment variables (set in Railway or a local .env file).
"""
import os

# Load .env file when running locally (ignored in production)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

# Meta API Configuration
ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
API_VERSION = "v21.0"

# OpenAI API Configuration (for AI image generation)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Email Notification Configuration
NOTIFY_EMAIL = os.environ["NOTIFY_EMAIL"]
NOTIFY_EMAIL_PASSWORD = os.environ["NOTIFY_EMAIL_PASSWORD"]

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN  = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM_NUMBER = os.environ["TWILIO_FROM_NUMBER"]
TWILIO_TO_NUMBER   = os.environ["TWILIO_TO_NUMBER"]
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

# Business Info
BUSINESS_NAME = "Clean Stream Pro Wash"
BUSINESS_ADDRESS = "6634 Avalon Dr SE, Caledonia, MI"
BUSINESS_SERVICES = [
    "House Washing",
    "Roof Washing",
    "Gutter Cleaning",
    "Driveway/Concrete Cleaning",
    "Deck/Fence Cleaning",
    "Window Cleaning",
    "Christmas Lighting Installation",
    "Christmas Lighting Removal",
]

# Targeting Configuration
TARGETING = {
    "geo_locations": {
        "custom_locations": [{
            "address_string": "6634 Avalon Dr SE, Caledonia, MI",
            "radius": 25,
            "distance_unit": "mile",
        }],
        "location_types": ["home", "recent"],
    },
    "excluded_geo_locations": {
        "cities": [
            {"key": "2418779", "name": "Big Rapids", "radius": 29, "distance_unit": "mile"},
            {"key": "2423945", "name": "Detroit", "radius": 50, "distance_unit": "mile"},
            {"key": "2430536", "name": "Kalamazoo", "radius": 10, "distance_unit": "mile"},
            {"key": "2431590", "name": "Lansing", "radius": 25, "distance_unit": "mile"},
            {"key": "2435925", "name": "Mount Pleasant", "radius": 29, "distance_unit": "mile"},
        ],
    },
    "age_min": 25,
    "age_max": 65,
}

# Performance Thresholds for optimization
OPTIMIZATION = {
    # Ads with CPL above this are considered underperforming
    "max_cost_per_lead": 25.00,
    # Ads with CPL below this are considered winners
    "winning_cost_per_lead": 15.00,
    # Minimum spend before evaluating (don't kill ads too early)
    "min_spend_before_eval": 15.00,
    # Minimum leads before evaluating
    "min_leads_before_eval": 0,
    # CTR below this = poor creative
    "min_ctr": 0.8,
    # Days of data to analyze
    "lookback_days": 30,
}
