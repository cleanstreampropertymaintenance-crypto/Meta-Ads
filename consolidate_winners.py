#!/usr/bin/env python3
"""
STEP 3: Consolidate winning ads into a single "Winners" campaign
- Creates a new campaign called "[Service] - Winners"
- Creates ad sets with your proven targeting
- Duplicates winning ad creatives into the new campaign
- Does NOT set budget without your approval

Usage: python3 consolidate_winners.py [--dry-run]
"""

import json
import sys
from meta_client import MetaAdsClient
from config import TARGETING, OPTIMIZATION

DRY_RUN = "--dry-run" in sys.argv


def load_optimization_results():
    try:
        with open("optimization_results.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: optimization_results.json not found. Run 'python3 optimize.py' first.")
        sys.exit(1)


def run_consolidation():
    client = MetaAdsClient()
    results = load_optimization_results()
    winners = results.get("winners", [])

    print("=" * 70)
    print("  CONSOLIDATE WINNERS INTO NEW CAMPAIGN")
    print(f"  Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print("=" * 70)

    if not winners:
        print("\n  No winning ads found. Nothing to consolidate.")
        print("  Tips: Lower your winning_cost_per_lead threshold in config.py,")
        print("  or run more ads to find winners.")
        return

    account_id = client.get_account_id()

    # Group winners by service/topic based on campaign or ad name
    service_groups = {}
    for ad in winners:
        # Try to detect service from name
        name_lower = ad["ad_name"].lower() + " " + ad["campaign_name"].lower()
        if "house wash" in name_lower or "pressure wash" in name_lower or "power wash" in name_lower:
            service = "House Washing"
        elif "roof" in name_lower:
            service = "Roof Washing"
        elif "gutter" in name_lower:
            service = "Gutter Cleaning"
        elif "driveway" in name_lower or "concrete" in name_lower:
            service = "Driveway Cleaning"
        elif "deck" in name_lower or "fence" in name_lower:
            service = "Deck & Fence"
        elif "window" in name_lower:
            service = "Window Cleaning"
        elif "christmas" in name_lower or "light" in name_lower or "holiday" in name_lower:
            service = "Christmas Lighting"
        else:
            service = "General"

        if service not in service_groups:
            service_groups[service] = []
        service_groups[service].append(ad)

    print(f"\n  Found {len(winners)} winning ads across {len(service_groups)} service categories:")
    for service, ads in service_groups.items():
        print(f"    {service}: {len(ads)} winning ads")

    if DRY_RUN:
        print("\n  DRY RUN - Would create:")
        for service, ads in service_groups.items():
            print(f"    Campaign: 'CSPW - {service} - Winners'")
            print(f"    Ad Set: '{service} - Proven Audience'")
            for ad in ads:
                print(f"      Ad: '{ad['ad_name']}' (CPL: ${ad['cpl']:.2f})")
        print("\n  Run without --dry-run to create these.")
        return

    # Create campaigns for each service group
    created = []
    for service, ads in service_groups.items():
        print(f"\n  Creating Winners campaign for: {service}")

        # Calculate suggested budget based on winner performance
        total_winner_spend = sum(a["spend"] for a in ads)
        total_winner_leads = sum(a["leads"] for a in ads)
        suggested_daily = max(10, round(total_winner_spend / 30, 2))  # Rough daily from 30-day spend

        # Create campaign (PAUSED - user must approve budget and activate)
        try:
            campaign = client.create_campaign(
                account_id,
                name=f"CSPW - {service} - Winners",
                objective="OUTCOME_LEADS",
                status="PAUSED",
            )
            campaign_id = campaign["id"]
            print(f"    ✓ Campaign created: {campaign_id}")

            # Create ad set with proven targeting
            adset = client.create_ad_set(
                account_id,
                campaign_id=campaign_id,
                name=f"{service} - Proven Audience - 25mi Caledonia",
                daily_budget=suggested_daily,
                targeting=TARGETING,
                optimization_goal="LEAD_GENERATION",
                status="PAUSED",
            )
            adset_id = adset["id"]
            print(f"    ✓ Ad Set created: {adset_id} (Daily budget: ${suggested_daily:.2f})")

            # Duplicate winning ads into new ad set
            for ad in ads:
                if ad.get("creative_id"):
                    try:
                        new_ad = client.create_ad(
                            account_id,
                            name=f"[Winner] {ad['ad_name']}",
                            adset_id=adset_id,
                            creative_id=ad["creative_id"],
                            status="PAUSED",
                        )
                        print(f"    ✓ Ad duplicated: {ad['ad_name']} → {new_ad['id']}")
                        created.append({
                            "service": service,
                            "campaign_id": campaign_id,
                            "adset_id": adset_id,
                            "ad_id": new_ad["id"],
                            "original_ad": ad["ad_name"],
                            "original_cpl": ad["cpl"],
                            "suggested_daily_budget": suggested_daily,
                        })
                    except Exception as e:
                        print(f"    ✗ Error duplicating {ad['ad_name']}: {e}")

        except Exception as e:
            print(f"    ✗ Error creating campaign: {e}")

    # Summary
    print(f"\n  {'=' * 50}")
    print(f"  CONSOLIDATION COMPLETE")
    print(f"  {'=' * 50}")
    print(f"  Campaigns created: {len(service_groups)}")
    print(f"  Ads duplicated: {len(created)}")
    print(f"\n  ⚠️  ALL NEW CAMPAIGNS ARE PAUSED")
    print(f"  Review in Ads Manager, then activate when ready.")
    print(f"  Budget suggestions are based on historical spend.")

    with open("consolidation_results.json", "w") as f:
        json.dump(created, f, indent=2)
    print(f"  Results saved to consolidation_results.json")


if __name__ == "__main__":
    run_consolidation()
