#!/usr/bin/env python3
"""
STEP 2: Optimize Meta Ads for Clean Stream Pro Wash
- Pauses underperforming ads (Grade F)
- Keeps decent ads running (Grade B)
- Identifies winners for consolidation (Grade A)
- Does NOT increase spend without confirmation

Usage: python3 optimize.py [--dry-run]
"""

import json
import sys
from meta_client import MetaAdsClient
from config import OPTIMIZATION

DRY_RUN = "--dry-run" in sys.argv


def load_audit_data():
    try:
        with open("audit_data.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: audit_data.json not found. Run 'python3 audit.py' first.")
        sys.exit(1)


def run_optimization():
    client = MetaAdsClient()
    ads = load_audit_data()

    print("=" * 70)
    print("  CLEAN STREAM PRO WASH - AD OPTIMIZATION")
    print(f"  Mode: {'DRY RUN (no changes)' if DRY_RUN else 'LIVE - Making changes!'}")
    print("=" * 70)

    # Categorize
    winners = [a for a in ads if a["grade"] == "A"]
    decent = [a for a in ads if a["grade"] == "B"]
    underperformers = [a for a in ads if a["grade"] == "C"]
    turn_off = [a for a in ads if a["grade"] == "F"]
    new_ads = [a for a in ads if a["grade"] == "NEW"]

    changes_made = []

    # --- TURN OFF F-grade ads ---
    if turn_off:
        print(f"\n  PAUSING {len(turn_off)} underperforming ads:")
        for ad in turn_off:
            cpl_str = f"${ad['cpl']:.2f}" if ad['cpl'] else "N/A"
            print(f"    Pausing: {ad['ad_name']} (CPL: {cpl_str}, Spend: ${ad['spend']:.2f}, Leads: {ad['leads']})")
            if not DRY_RUN:
                try:
                    if ad["status"] != "PAUSED":
                        client.update_ad(ad["ad_id"], status="PAUSED")
                        changes_made.append(f"PAUSED ad: {ad['ad_name']} ({ad['ad_id']})")
                        print(f"      ✓ Paused")
                    else:
                        print(f"      (Already paused)")
                except Exception as e:
                    print(f"      ✗ Error: {e}")

    # --- PAUSE C-grade ads with high spend ---
    high_spend_c = [a for a in underperformers if a["spend"] > OPTIMIZATION["max_cost_per_lead"] * 2]
    if high_spend_c:
        print(f"\n  PAUSING {len(high_spend_c)} high-spend underperformers:")
        for ad in high_spend_c:
            cpl_str = f"${ad['cpl']:.2f}" if ad['cpl'] else "N/A"
            print(f"    Pausing: {ad['ad_name']} (CPL: {cpl_str}, Spend: ${ad['spend']:.2f})")
            if not DRY_RUN:
                try:
                    if ad["status"] != "PAUSED":
                        client.update_ad(ad["ad_id"], status="PAUSED")
                        changes_made.append(f"PAUSED ad: {ad['ad_name']} ({ad['ad_id']})")
                        print(f"      ✓ Paused")
                    else:
                        print(f"      (Already paused)")
                except Exception as e:
                    print(f"      ✗ Error: {e}")

    # --- Report winners ---
    if winners:
        print(f"\n  WINNING ADS (keep running, consolidate into winners campaign):")
        for ad in winners:
            print(f"    ★ {ad['ad_name']} | CPL: ${ad['cpl']:.2f} | Leads: {ad['leads']} | Spend: ${ad['spend']:.2f}")

    # --- Report decent ---
    if decent:
        print(f"\n  DECENT ADS (keep running, monitor closely):")
        for ad in decent:
            cpl_str = f"${ad['cpl']:.2f}" if ad['cpl'] else "N/A"
            print(f"    → {ad['ad_name']} | CPL: {cpl_str} | Leads: {ad['leads']} | Spend: ${ad['spend']:.2f}")

    # --- Report new ---
    if new_ads:
        print(f"\n  NEW ADS (not enough data, let them run):")
        for ad in new_ads:
            print(f"    ? {ad['ad_name']} | Spend: ${ad['spend']:.2f}")

    # --- Summary ---
    print(f"\n  {'=' * 50}")
    print(f"  OPTIMIZATION SUMMARY")
    print(f"  {'=' * 50}")
    print(f"  Ads paused: {len(changes_made)}")
    print(f"  Winners identified: {len(winners)}")
    print(f"  Ads kept running: {len(decent) + len(new_ads)}")

    # Calculate savings
    paused_spend = sum(a["spend"] for a in turn_off + high_spend_c)
    paused_leads = sum(a["leads"] for a in turn_off + high_spend_c)
    print(f"  Budget freed from paused ads: ~${paused_spend:.2f}/period ({paused_leads} leads)")

    if winners:
        winner_spend = sum(a["spend"] for a in winners)
        winner_leads = sum(a["leads"] for a in winners)
        winner_cpl = winner_spend / winner_leads if winner_leads > 0 else 0
        print(f"  Winner avg CPL: ${winner_cpl:.2f}")
        print(f"\n  RECOMMENDATION: Move freed budget (${paused_spend:.2f}) to winning ads")
        print(f"  Next step: Run 'python3 consolidate_winners.py' to create Winners campaign")

    # Save optimization results
    results = {
        "winners": winners,
        "decent": decent,
        "underperformers": underperformers,
        "turned_off": turn_off + high_spend_c,
        "new_ads": new_ads,
        "changes": changes_made,
    }
    with open("optimization_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to optimization_results.json")


if __name__ == "__main__":
    run_optimization()
