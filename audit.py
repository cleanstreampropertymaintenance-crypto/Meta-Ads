#!/usr/bin/env python3
"""
STEP 1: Audit all Meta Ads for Clean Stream Pro Wash
Run this first to see all campaigns, ad sets, ads, and their performance.
Outputs a detailed report and saves raw data for the optimizer.

Usage: python3 audit.py
"""

import json
import sys
from datetime import datetime
from meta_client import MetaAdsClient
from config import OPTIMIZATION

def extract_leads(actions):
    """Extract lead count from actions list."""
    if not actions:
        return 0
    for action in actions:
        if action.get("action_type") in ("lead", "onsite_conversion.lead_grouped", "offsite_conversion.fb_pixel_lead"):
            return int(action.get("value", 0))
    return 0

def extract_cpl(cost_per_action_type):
    """Extract cost per lead from cost_per_action_type."""
    if not cost_per_action_type:
        return None
    for action in cost_per_action_type:
        if action.get("action_type") in ("lead", "onsite_conversion.lead_grouped", "offsite_conversion.fb_pixel_lead"):
            return float(action.get("value", 0))
    return None

def print_divider(char="=", length=80):
    print(char * length)

def print_header(text):
    print_divider()
    print(f"  {text}")
    print_divider()

def grade_ad(spend, leads, cpl, ctr):
    """Grade an ad: A (winner), B (decent), C (underperformer), F (turn off)."""
    thresholds = OPTIMIZATION

    if spend < thresholds["min_spend_before_eval"]:
        return "NEW", "Not enough data yet"

    if leads == 0:
        if spend > thresholds["max_cost_per_lead"]:
            return "F", f"Spent ${spend:.2f} with ZERO leads - TURN OFF"
        return "C", f"No leads yet, spent ${spend:.2f}"

    if cpl and cpl <= thresholds["winning_cost_per_lead"]:
        return "A", f"WINNER! CPL ${cpl:.2f} - Push more budget here"
    elif cpl and cpl <= thresholds["max_cost_per_lead"]:
        return "B", f"Decent CPL ${cpl:.2f} - Keep running, monitor"
    elif cpl and cpl > thresholds["max_cost_per_lead"]:
        if cpl > thresholds["max_cost_per_lead"] * 1.5:
            return "F", f"CPL ${cpl:.2f} way too high - TURN OFF"
        return "C", f"CPL ${cpl:.2f} above target - Consider pausing"

    if ctr and float(ctr) < thresholds["min_ctr"]:
        return "C", f"CTR {ctr}% too low - Creative needs work"

    return "B", "Average performance"


def run_audit():
    client = MetaAdsClient()
    days = OPTIMIZATION["lookback_days"]

    print_header(f"CLEAN STREAM PRO WASH - META ADS AUDIT ({days}-Day Lookback)")
    print(f"  Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # Get account
    try:
        account_id = client.get_account_id()
        print(f"  Ad Account: {account_id}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Get pages
    try:
        pages = client.get_pages()
        for page in pages.get("data", []):
            print(f"  Page: {page['name']} (ID: {page['id']})")
    except Exception:
        pass

    print()

    # --- Campaigns ---
    print_header("CAMPAIGNS")
    campaigns = client.get_campaigns(account_id)
    campaign_data = campaigns.get("data", [])

    all_ads_data = []  # Collect for optimizer

    if not campaign_data:
        print("  No campaigns found.")
        return

    for campaign in campaign_data:
        cid = campaign["id"]
        print(f"\n  Campaign: {campaign['name']}")
        print(f"  ID: {cid} | Status: {campaign['status']} | Objective: {campaign.get('objective', 'N/A')}")

        daily = campaign.get("daily_budget")
        if daily:
            print(f"  Daily Budget: ${int(daily)/100:.2f}")
        lifetime = campaign.get("lifetime_budget")
        if lifetime:
            print(f"  Lifetime Budget: ${int(lifetime)/100:.2f}")

        # Campaign insights
        try:
            insights = client.get_campaign_insights(cid, days)
            if insights.get("data"):
                i = insights["data"][0]
                spend = float(i.get("spend", 0))
                impressions = int(i.get("impressions", 0))
                clicks = int(i.get("clicks", 0))
                ctr = i.get("ctr", "0")
                leads = extract_leads(i.get("actions"))
                cpl = extract_cpl(i.get("cost_per_action_type"))

                print(f"  Spend: ${spend:.2f} | Impressions: {impressions:,} | Clicks: {clicks:,}")
                print(f"  CTR: {float(ctr):.2f}% | Leads: {leads} | CPL: ${cpl:.2f}" if cpl else f"  CTR: {float(ctr):.2f}% | Leads: {leads} | CPL: N/A")
        except Exception as e:
            print(f"  (No insights: {e})")

        # --- Ad Sets in this campaign ---
        print(f"\n  --- Ad Sets ---")
        adsets = client.get_ad_sets(campaign_id=cid)
        adset_data = adsets.get("data", [])

        if not adset_data:
            print("    No ad sets found.")
            continue

        for adset in adset_data:
            asid = adset["id"]
            print(f"\n    Ad Set: {adset['name']}")
            print(f"    ID: {asid} | Status: {adset['status']}")

            daily_b = adset.get("daily_budget")
            if daily_b:
                print(f"    Daily Budget: ${int(daily_b)/100:.2f}")

            # Check targeting
            targeting = adset.get("targeting", {})
            geo = targeting.get("geo_locations", {})
            age_min = targeting.get("age_min")
            age_max = targeting.get("age_max")
            if age_min or age_max:
                print(f"    Age: {age_min}-{age_max}")
            if geo:
                custom_locs = geo.get("custom_locations", [])
                for loc in custom_locs:
                    print(f"    Location: {loc.get('address_string', 'Custom')} ({loc.get('radius', '?')} {loc.get('distance_unit', 'mi')})")

            # Ad set insights
            try:
                insights = client.get_adset_insights(asid, days)
                if insights.get("data"):
                    i = insights["data"][0]
                    spend = float(i.get("spend", 0))
                    impressions = int(i.get("impressions", 0))
                    clicks = int(i.get("clicks", 0))
                    ctr = i.get("ctr", "0")
                    leads = extract_leads(i.get("actions"))
                    cpl = extract_cpl(i.get("cost_per_action_type"))
                    print(f"    Spend: ${spend:.2f} | Impressions: {impressions:,} | Clicks: {clicks:,}")
                    print(f"    CTR: {float(ctr):.2f}% | Leads: {leads} | CPL: ${cpl:.2f}" if cpl else f"    CTR: {float(ctr):.2f}% | Leads: {leads}")
            except Exception:
                pass

            # --- Ads in this ad set ---
            print(f"\n    --- Ads ---")
            ads = client.get_ads(adset_id=asid)
            ads_data = ads.get("data", [])

            if not ads_data:
                print("      No ads found.")
                continue

            for ad in ads_data:
                aid = ad["id"]
                print(f"\n      Ad: {ad['name']}")
                print(f"      ID: {aid} | Status: {ad['status']}")

                # Get creative details
                creative_ref = ad.get("creative", {})
                creative_id = creative_ref.get("id")
                if creative_id:
                    try:
                        creative = client.get_creative_details(creative_id)
                        if creative.get("body"):
                            body_preview = creative["body"][:100] + "..." if len(creative.get("body", "")) > 100 else creative.get("body", "")
                            print(f"      Creative Body: {body_preview}")
                        if creative.get("title"):
                            print(f"      Creative Title: {creative['title']}")
                        if creative.get("call_to_action_type"):
                            print(f"      CTA: {creative['call_to_action_type']}")
                    except Exception:
                        pass

                # Ad insights
                try:
                    insights = client.get_ad_insights(aid, days)
                    if insights.get("data"):
                        i = insights["data"][0]
                        spend = float(i.get("spend", 0))
                        impressions = int(i.get("impressions", 0))
                        clicks = int(i.get("clicks", 0))
                        ctr = i.get("ctr", "0")
                        leads = extract_leads(i.get("actions"))
                        cpl = extract_cpl(i.get("cost_per_action_type"))
                        quality = i.get("quality_ranking", "N/A")
                        engagement = i.get("engagement_rate_ranking", "N/A")
                        conversion = i.get("conversion_rate_ranking", "N/A")

                        grade, reason = grade_ad(spend, leads, cpl, ctr)

                        print(f"      Spend: ${spend:.2f} | Impressions: {impressions:,} | Clicks: {clicks:,}")
                        print(f"      CTR: {float(ctr):.2f}% | Leads: {leads} | CPL: ${cpl:.2f}" if cpl else f"      CTR: {float(ctr):.2f}% | Leads: {leads}")
                        print(f"      Quality: {quality} | Engagement: {engagement} | Conversion: {conversion}")
                        print(f"      >>> GRADE: {grade} - {reason}")

                        all_ads_data.append({
                            "ad_id": aid,
                            "ad_name": ad["name"],
                            "adset_id": asid,
                            "adset_name": adset["name"],
                            "campaign_id": cid,
                            "campaign_name": campaign["name"],
                            "status": ad["status"],
                            "spend": spend,
                            "impressions": impressions,
                            "clicks": clicks,
                            "ctr": float(ctr),
                            "leads": leads,
                            "cpl": cpl,
                            "grade": grade,
                            "reason": reason,
                            "quality_ranking": quality,
                            "engagement_ranking": engagement,
                            "conversion_ranking": conversion,
                            "creative_id": creative_id,
                        })
                    else:
                        print("      (No delivery data)")
                        all_ads_data.append({
                            "ad_id": aid,
                            "ad_name": ad["name"],
                            "adset_id": asid,
                            "adset_name": adset["name"],
                            "campaign_id": cid,
                            "campaign_name": campaign["name"],
                            "status": ad["status"],
                            "spend": 0, "impressions": 0, "clicks": 0,
                            "ctr": 0, "leads": 0, "cpl": None,
                            "grade": "NEW", "reason": "No delivery data",
                            "creative_id": creative_id,
                        })
                except Exception as e:
                    print(f"      (No insights: {e})")

    # --- Summary ---
    print()
    print_header("AUDIT SUMMARY")

    winners = [a for a in all_ads_data if a["grade"] == "A"]
    decent = [a for a in all_ads_data if a["grade"] == "B"]
    underperformers = [a for a in all_ads_data if a["grade"] == "C"]
    turn_off = [a for a in all_ads_data if a["grade"] == "F"]
    new_ads = [a for a in all_ads_data if a["grade"] == "NEW"]

    print(f"  Total Ads Analyzed: {len(all_ads_data)}")
    print(f"  🏆 Winners (A):        {len(winners)}")
    print(f"  ✅ Decent (B):         {len(decent)}")
    print(f"  ⚠️  Underperformers (C): {len(underperformers)}")
    print(f"  ❌ Turn Off (F):       {len(turn_off)}")
    print(f"  🆕 New/Not Enough Data: {len(new_ads)}")

    if winners:
        print(f"\n  --- WINNING ADS ---")
        for a in winners:
            print(f"  {a['ad_name']} | CPL: ${a['cpl']:.2f} | Leads: {a['leads']} | Spend: ${a['spend']:.2f}")

    if turn_off:
        print(f"\n  --- SHOULD TURN OFF ---")
        for a in turn_off:
            cpl_str = f"${a['cpl']:.2f}" if a['cpl'] else "N/A"
            print(f"  {a['ad_name']} | CPL: {cpl_str} | Leads: {a['leads']} | Spend: ${a['spend']:.2f}")

    total_spend = sum(a["spend"] for a in all_ads_data)
    total_leads = sum(a["leads"] for a in all_ads_data)
    avg_cpl = total_spend / total_leads if total_leads > 0 else 0

    print(f"\n  Total Spend: ${total_spend:.2f}")
    print(f"  Total Leads: {total_leads}")
    print(f"  Overall CPL: ${avg_cpl:.2f}" if total_leads > 0 else "  Overall CPL: N/A")

    # Save data for optimizer
    with open("audit_data.json", "w") as f:
        json.dump(all_ads_data, f, indent=2)
    print(f"\n  Raw data saved to audit_data.json")
    print(f"  Next step: Run 'python3 optimize.py' to auto-optimize")
    print_divider()


if __name__ == "__main__":
    run_audit()
