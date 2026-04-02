"""
Configuration for Clean Stream Pro Wash Meta Ads Management
"""

# Meta API Configuration
ACCESS_TOKEN = "EAAKj3HprtxsBROcBhHCVEDluSnqiUXR7uuB536e1uZCpCPjWueINbQW0EQmYPJhrTGWi7Vz1aSKBeU5JtsmuGd6Dwv3ZBjH3cVPOiAwgrzwps0g2zhSdQiabENm0Yy7yTU5pbbHVvVokZCngARzCmwdrBzEpZAXD9F1hwAUEbZBy3ZAtOZBxcKVYnlyLLBR7QZDZD"
API_VERSION = "v21.0"
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
        "regions": [
            {"key": "DMA:563", "name": "Muskegon County"},
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
