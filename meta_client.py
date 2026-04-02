"""
Meta Graph API Client for Clean Stream Pro Wash
Handles all API communication with Facebook/Meta Ads
"""

import requests
import json
import time
from datetime import datetime, timedelta
from config import ACCESS_TOKEN, API_VERSION, BASE_URL


class MetaAdsClient:
    def __init__(self, access_token=None):
        self.access_token = access_token or ACCESS_TOKEN
        self.base_url = BASE_URL
        self.session = requests.Session()

    def _request(self, method, endpoint, params=None, data=None):
        """Make an API request with automatic token injection and error handling."""
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        params["access_token"] = self.access_token

        if method == "GET":
            resp = self.session.get(url, params=params)
        elif method == "POST":
            if data is None:
                data = {}
            data["access_token"] = self.access_token
            resp = self.session.post(url, data=data)
        elif method == "DELETE":
            resp = self.session.delete(url, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")

        result = resp.json()
        if "error" in result:
            raise Exception(f"Meta API Error: {result['error'].get('message', result['error'])}")
        return result

    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._request("POST", endpoint, data=data)

    def delete(self, endpoint, params=None):
        return self._request("DELETE", endpoint, params=params)

    # --- Account Methods ---

    def get_ad_accounts(self):
        """Get all ad accounts accessible with this token."""
        return self.get("me/adaccounts", {
            "fields": "name,account_id,account_status,currency,balance,amount_spent,business_name"
        })

    def get_account_id(self):
        """Get the first active ad account ID."""
        accounts = self.get_ad_accounts()
        for acct in accounts.get("data", []):
            if acct.get("account_status") == 1:  # 1 = ACTIVE
                return acct["id"]
        # Fall back to first account
        if accounts.get("data"):
            return accounts["data"][0]["id"]
        raise Exception("No ad accounts found")

    # --- Campaign Methods ---

    def get_campaigns(self, account_id, status_filter=None):
        """Get all campaigns for an account."""
        params = {
            "fields": "name,status,objective,daily_budget,lifetime_budget,budget_remaining,created_time,updated_time,buying_type",
            "limit": 100,
        }
        if status_filter:
            params["effective_status"] = json.dumps(status_filter)
        return self.get(f"{account_id}/campaigns", params)

    def get_campaign_insights(self, campaign_id, days=30):
        """Get performance insights for a campaign."""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        until = datetime.now().strftime("%Y-%m-%d")
        return self.get(f"{campaign_id}/insights", {
            "fields": "campaign_name,impressions,reach,clicks,cpc,cpm,ctr,spend,actions,cost_per_action_type,frequency",
            "time_range": json.dumps({"since": since, "until": until}),
        })

    def create_campaign(self, account_id, name, objective="OUTCOME_LEADS", daily_budget=None,
                        status="PAUSED", special_ad_categories=None):
        """Create a new campaign."""
        data = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": json.dumps(special_ad_categories or []),
        }
        if daily_budget:
            data["daily_budget"] = int(daily_budget * 100)  # Convert to cents
        return self.post(f"{account_id}/campaigns", data)

    def update_campaign(self, campaign_id, **kwargs):
        """Update a campaign's settings."""
        data = {}
        for key, value in kwargs.items():
            if key == "daily_budget":
                data[key] = int(value * 100)
            elif key == "status":
                data[key] = value
            else:
                data[key] = value
        return self.post(campaign_id, data)

    # --- Ad Set Methods ---

    def get_ad_sets(self, account_id=None, campaign_id=None, status_filter=None):
        """Get ad sets for an account or campaign."""
        parent = campaign_id or account_id
        endpoint = f"{parent}/adsets"
        params = {
            "fields": "name,status,campaign_id,daily_budget,lifetime_budget,budget_remaining,targeting,optimization_goal,billing_event,bid_strategy,start_time,end_time,created_time",
            "limit": 100,
        }
        if status_filter:
            params["effective_status"] = json.dumps(status_filter)
        return self.get(endpoint, params)

    def get_adset_insights(self, adset_id, days=30):
        """Get performance insights for an ad set."""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        until = datetime.now().strftime("%Y-%m-%d")
        return self.get(f"{adset_id}/insights", {
            "fields": "adset_name,impressions,reach,clicks,cpc,cpm,ctr,spend,actions,cost_per_action_type,frequency",
            "time_range": json.dumps({"since": since, "until": until}),
        })

    def create_ad_set(self, account_id, campaign_id, name, daily_budget, targeting,
                      optimization_goal="LEAD_GENERATION", billing_event="IMPRESSIONS",
                      bid_strategy="LOWEST_COST_WITHOUT_CAP", status="PAUSED"):
        """Create a new ad set."""
        data = {
            "name": name,
            "campaign_id": campaign_id,
            "daily_budget": int(daily_budget * 100),
            "targeting": json.dumps(targeting),
            "optimization_goal": optimization_goal,
            "billing_event": billing_event,
            "bid_strategy": bid_strategy,
            "status": status,
        }
        return self.post(f"{account_id}/adsets", data)

    def update_ad_set(self, adset_id, **kwargs):
        """Update an ad set."""
        data = {}
        for key, value in kwargs.items():
            if key in ("daily_budget", "lifetime_budget"):
                data[key] = int(value * 100)
            elif key == "targeting":
                data[key] = json.dumps(value)
            else:
                data[key] = value
        return self.post(adset_id, data)

    # --- Ad Methods ---

    def get_ads(self, account_id=None, adset_id=None, status_filter=None):
        """Get ads for an account or ad set."""
        parent = adset_id or account_id
        endpoint = f"{parent}/ads"
        params = {
            "fields": "name,status,adset_id,campaign_id,creative,created_time,updated_time",
            "limit": 100,
        }
        if status_filter:
            params["effective_status"] = json.dumps(status_filter)
        return self.get(endpoint, params)

    def get_ad_insights(self, ad_id, days=30):
        """Get performance insights for a specific ad."""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        until = datetime.now().strftime("%Y-%m-%d")
        return self.get(f"{ad_id}/insights", {
            "fields": "ad_name,impressions,reach,clicks,cpc,cpm,ctr,spend,actions,cost_per_action_type,frequency,quality_ranking,engagement_rate_ranking,conversion_rate_ranking",
            "time_range": json.dumps({"since": since, "until": until}),
        })

    def create_ad(self, account_id, name, adset_id, creative_id, status="PAUSED"):
        """Create a new ad."""
        data = {
            "name": name,
            "adset_id": adset_id,
            "creative": json.dumps({"creative_id": creative_id}),
            "status": status,
        }
        return self.post(f"{account_id}/ads", data)

    def update_ad(self, ad_id, **kwargs):
        """Update an ad."""
        return self.post(ad_id, kwargs)

    # --- Creative Methods ---

    def get_ad_creatives(self, account_id):
        """Get all ad creatives for an account."""
        return self.get(f"{account_id}/adcreatives", {
            "fields": "name,title,body,call_to_action_type,image_url,thumbnail_url,object_story_spec,link_url,status",
            "limit": 100,
        })

    def get_creative_details(self, creative_id):
        """Get details for a specific creative."""
        return self.get(creative_id, {
            "fields": "name,title,body,call_to_action_type,image_url,thumbnail_url,object_story_spec,link_url,status,effective_object_story_id"
        })

    def create_ad_creative(self, account_id, name, page_id, message, link=None,
                           image_hash=None, image_url=None, call_to_action=None,
                           lead_gen_form_id=None):
        """Create a new ad creative for lead gen."""
        object_story_spec = {
            "page_id": page_id,
            "link_data": {
                "message": message,
                "link": link or f"https://facebook.com/{page_id}",
            }
        }

        if image_hash:
            object_story_spec["link_data"]["image_hash"] = image_hash
        if call_to_action:
            cta = {"type": call_to_action}
            if lead_gen_form_id:
                cta["value"] = {"lead_gen_form_id": lead_gen_form_id}
            object_story_spec["link_data"]["call_to_action"] = cta

        data = {
            "name": name,
            "object_story_spec": json.dumps(object_story_spec),
        }
        return self.post(f"{account_id}/adcreatives", data)

    def upload_image(self, account_id, image_path):
        """Upload an image and get its hash."""
        url = f"{self.base_url}/{account_id}/adimages"
        with open(image_path, "rb") as f:
            resp = self.session.post(url, files={"filename": f},
                                     data={"access_token": self.access_token})
        result = resp.json()
        if "error" in result:
            raise Exception(f"Image upload error: {result['error']}")
        images = result.get("images", {})
        for key, val in images.items():
            return val.get("hash")
        return None

    # --- Lead Form Methods ---

    def get_lead_forms(self, page_id):
        """Get lead forms for a page."""
        return self.get(f"{page_id}/leadgen_forms", {
            "fields": "id,name,status,questions,privacy_policy,thank_you_page,created_time"
        })

    def create_lead_form(self, page_id, name, questions, privacy_policy_url,
                         thank_you_message="Thanks! We'll be in touch shortly.",
                         context_card=None):
        """Create a new lead form."""
        data = {
            "name": name,
            "questions": json.dumps(questions),
            "privacy_policy": json.dumps({"url": privacy_policy_url}),
            "thank_you_page": json.dumps({
                "title": "Thank You!",
                "body": thank_you_message,
            }),
        }
        if context_card:
            data["context_card"] = json.dumps(context_card)
        return self.post(f"{page_id}/leadgen_forms", data)

    # --- Pages ---

    def get_pages(self):
        """Get pages managed by this token."""
        return self.get("me/accounts", {
            "fields": "name,id,access_token,category"
        })

    # --- Utility ---

    def paginate_all(self, initial_result):
        """Get all pages of results."""
        all_data = initial_result.get("data", [])
        next_url = initial_result.get("paging", {}).get("next")
        while next_url:
            resp = self.session.get(next_url).json()
            all_data.extend(resp.get("data", []))
            next_url = resp.get("paging", {}).get("next")
        return all_data
