#!/usr/bin/env python3
"""
STEP 4: Create new lead form ads for Clean Stream Pro Wash
- Creates lead gen campaigns with proper targeting
- Creates lead forms based on your existing house washing template
- Uploads images and creates ad creatives
- All created as PAUSED until you approve

Usage:
  python3 create_ads.py --service "House Washing" --image path/to/image.jpg
  python3 create_ads.py --service "Christmas Lighting" --image path/to/image.jpg
  python3 create_ads.py --list-services
  python3 create_ads.py --create-lead-form "Roof Washing"
"""

import argparse
import json
import sys
from meta_client import MetaAdsClient
from config import TARGETING, BUSINESS_NAME, BUSINESS_SERVICES

# --- Lead Form Templates ---
# Based on the existing house washing lead form pattern
LEAD_FORM_TEMPLATES = {
    "House Washing": {
        "name": "CSPW - House Washing Lead Form",
        "questions": [
            {"type": "FULL_NAME"},
            {"type": "EMAIL"},
            {"type": "PHONE"},
            {
                "type": "CUSTOM",
                "key": "square_footage",
                "label": "What is the approximate square footage of your home?",
                "options": [
                    {"value": "Under 1,500 sq ft"},
                    {"value": "1,500 - 2,500 sq ft"},
                    {"value": "2,500 - 3,500 sq ft"},
                    {"value": "3,500+ sq ft"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "home_type",
                "label": "What type of siding does your home have?",
                "options": [
                    {"value": "Vinyl"},
                    {"value": "Brick"},
                    {"value": "Wood"},
                    {"value": "Stucco"},
                    {"value": "Other/Not Sure"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "timeline",
                "label": "When would you like the service done?",
                "options": [
                    {"value": "ASAP - This week"},
                    {"value": "Within 2 weeks"},
                    {"value": "Within a month"},
                    {"value": "Just getting a quote"},
                ]
            },
        ],
        "thank_you": "Thanks for reaching out! We'll contact you within 24 hours with a free quote. - Clean Stream Pro Wash",
        "context_card": {
            "title": "Free House Washing Quote",
            "content": [
                "Get a free, no-obligation quote",
                "Soft wash safe for all siding types",
                "Fully insured & professional service",
                "Serving the greater Grand Rapids area",
            ],
        },
    },
    "Roof Washing": {
        "name": "CSPW - Roof Washing Lead Form",
        "questions": [
            {"type": "FULL_NAME"},
            {"type": "EMAIL"},
            {"type": "PHONE"},
            {
                "type": "CUSTOM",
                "key": "roof_type",
                "label": "What type of roof do you have?",
                "options": [
                    {"value": "Asphalt Shingles"},
                    {"value": "Metal"},
                    {"value": "Cedar/Wood"},
                    {"value": "Tile"},
                    {"value": "Not Sure"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "roof_issue",
                "label": "What issues are you seeing?",
                "options": [
                    {"value": "Black streaks/stains"},
                    {"value": "Moss or algae growth"},
                    {"value": "General dirtiness"},
                    {"value": "Preventative cleaning"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "timeline",
                "label": "When would you like the service done?",
                "options": [
                    {"value": "ASAP - This week"},
                    {"value": "Within 2 weeks"},
                    {"value": "Within a month"},
                    {"value": "Just getting a quote"},
                ]
            },
        ],
        "thank_you": "Thanks! We'll reach out within 24 hours with your free roof washing quote. - Clean Stream Pro Wash",
        "context_card": {
            "title": "Free Roof Washing Quote",
            "content": [
                "Safe soft wash - no pressure damage",
                "Removes black streaks, moss & algae",
                "Extends roof life by years",
                "Free quote, no obligation",
            ],
        },
    },
    "Gutter Cleaning": {
        "name": "CSPW - Gutter Cleaning Lead Form",
        "questions": [
            {"type": "FULL_NAME"},
            {"type": "EMAIL"},
            {"type": "PHONE"},
            {
                "type": "CUSTOM",
                "key": "stories",
                "label": "How many stories is your home?",
                "options": [
                    {"value": "1 story"},
                    {"value": "2 stories"},
                    {"value": "3+ stories"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "gutter_length",
                "label": "Approximate linear feet of gutters? (Don't worry if unsure)",
                "options": [
                    {"value": "Small home (under 150 ft)"},
                    {"value": "Medium home (150-250 ft)"},
                    {"value": "Large home (250+ ft)"},
                    {"value": "Not sure"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "timeline",
                "label": "When would you like the service done?",
                "options": [
                    {"value": "ASAP - This week"},
                    {"value": "Within 2 weeks"},
                    {"value": "Within a month"},
                    {"value": "Just getting a quote"},
                ]
            },
        ],
        "thank_you": "Thanks! We'll get back to you within 24 hours with a free gutter cleaning quote. - Clean Stream Pro Wash",
        "context_card": {
            "title": "Free Gutter Cleaning Quote",
            "content": [
                "Complete cleanout & flush",
                "Before/after photos provided",
                "Prevent water damage to your home",
                "Fast, professional service",
            ],
        },
    },
    "Driveway/Concrete Cleaning": {
        "name": "CSPW - Driveway Cleaning Lead Form",
        "questions": [
            {"type": "FULL_NAME"},
            {"type": "EMAIL"},
            {"type": "PHONE"},
            {
                "type": "CUSTOM",
                "key": "surface_type",
                "label": "What surfaces need cleaning?",
                "options": [
                    {"value": "Driveway only"},
                    {"value": "Patio/Walkways"},
                    {"value": "Driveway + Walkways"},
                    {"value": "Large concrete area"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "size",
                "label": "Approximate size of the area?",
                "options": [
                    {"value": "Small (under 500 sq ft)"},
                    {"value": "Medium (500-1000 sq ft)"},
                    {"value": "Large (1000+ sq ft)"},
                    {"value": "Not sure"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "timeline",
                "label": "When would you like the service done?",
                "options": [
                    {"value": "ASAP - This week"},
                    {"value": "Within 2 weeks"},
                    {"value": "Within a month"},
                    {"value": "Just getting a quote"},
                ]
            },
        ],
        "thank_you": "Thanks! We'll reach out within 24 hours with your free quote. - Clean Stream Pro Wash",
        "context_card": {
            "title": "Free Concrete Cleaning Quote",
            "content": [
                "Removes oil, mold, and years of grime",
                "Professional surface cleaning",
                "Instant curb appeal boost",
                "Free quote, no obligation",
            ],
        },
    },
    "Christmas Lighting": {
        "name": "CSPW - Christmas Lighting Lead Form",
        "questions": [
            {"type": "FULL_NAME"},
            {"type": "EMAIL"},
            {"type": "PHONE"},
            {
                "type": "CUSTOM",
                "key": "service_type",
                "label": "What service are you interested in?",
                "options": [
                    {"value": "Full design & installation"},
                    {"value": "Installation only (I have lights)"},
                    {"value": "Removal only"},
                    {"value": "Design consultation"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "home_size",
                "label": "Approximate roofline footage?",
                "options": [
                    {"value": "Small (under 100 ft)"},
                    {"value": "Medium (100-200 ft)"},
                    {"value": "Large (200-300 ft)"},
                    {"value": "Very large (300+ ft)"},
                    {"value": "Not sure - need measurement"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "extras",
                "label": "Interested in any extras?",
                "options": [
                    {"value": "Trees/bushes wrapped"},
                    {"value": "Yard displays"},
                    {"value": "Roofline only"},
                    {"value": "Full property design"},
                ]
            },
            {
                "type": "CUSTOM",
                "key": "timeline",
                "label": "When do you want lights installed?",
                "options": [
                    {"value": "Before Thanksgiving"},
                    {"value": "First week of December"},
                    {"value": "Mid December"},
                    {"value": "Flexible/Just getting a quote"},
                ]
            },
        ],
        "thank_you": "Thanks! We'll reach out within 24 hours to schedule your free design consultation. - Clean Stream Pro Wash",
        "context_card": {
            "title": "Professional Christmas Lighting",
            "content": [
                "Custom design for your home",
                "Professional installation & removal",
                "Commercial-grade LED lights",
                "Free design consultation",
            ],
        },
    },
}

# --- Ad Copy Templates ---
AD_COPY = {
    "House Washing": [
        {
            "headline": "Your Home Deserves a Fresh Look",
            "body": "Is your home's siding covered in dirt, algae, or mildew? Clean Stream Pro Wash uses a safe soft wash process that makes your home look brand new — without any damage to your siding.\n\n✅ Safe for all siding types\n✅ Removes years of buildup\n✅ Fully insured\n✅ Free quotes\n\nServing Caledonia, Grand Rapids, Byron Center & surrounding areas within 25 miles.\n\nTap 'Get Quote' for your FREE estimate!",
            "cta": "GET_QUOTE",
        },
        {
            "headline": "When Was The Last Time Your House Was Washed?",
            "body": "Most homeowners don't realize how much dirt, mold, and algae builds up on their home — until they see the difference a professional wash makes.\n\nClean Stream Pro Wash brings your home back to life with our safe soft wash process.\n\n🏠 Before & after results you have to see\n💰 Affordable pricing\n📋 Free, no-pressure quotes\n\nClick below to get your free quote today!",
            "cta": "GET_QUOTE",
        },
        {
            "headline": "FREE House Washing Quote - Caledonia Area",
            "body": "Your neighbors are already getting their homes washed this spring. Don't let your house be the one on the block that stands out — for the wrong reasons.\n\nClean Stream Pro Wash offers:\n→ Soft wash safe for vinyl, brick, wood & more\n→ Same-week scheduling available\n→ 100% satisfaction guaranteed\n\nGet your FREE quote in under 60 seconds 👇",
            "cta": "GET_QUOTE",
        },
    ],
    "Roof Washing": [
        {
            "headline": "Black Streaks On Your Roof?",
            "body": "Those ugly black streaks aren't just dirt — they're algae that's eating away at your shingles and shortening your roof's lifespan.\n\nClean Stream Pro Wash removes them safely with our soft wash process. No pressure, no damage.\n\n✅ Extends roof life\n✅ Improves curb appeal\n✅ Safe for all roof types\n✅ Free estimates\n\nTap below for your FREE roof washing quote!",
            "cta": "GET_QUOTE",
        },
    ],
    "Gutter Cleaning": [
        {
            "headline": "Clogged Gutters = Expensive Repairs",
            "body": "Don't wait until water is pouring over the sides. Clogged gutters cause foundation damage, basement flooding, and rotting fascia.\n\nClean Stream Pro Wash offers fast, thorough gutter cleaning:\n\n✅ Complete cleanout & downspout flush\n✅ Before/after photos\n✅ Affordable pricing\n✅ Free quotes\n\nProtect your home — get your free quote today 👇",
            "cta": "GET_QUOTE",
        },
    ],
    "Driveway/Concrete Cleaning": [
        {
            "headline": "Your Driveway Looked Great Once. It Can Again.",
            "body": "Oil stains, tire marks, mold, and years of grime don't stand a chance against Clean Stream Pro Wash.\n\nOur professional pressure washing transforms your concrete and gives your home instant curb appeal.\n\n✅ Driveways, patios, walkways\n✅ Oil stain removal\n✅ Fast & affordable\n✅ Free estimates\n\nGet your FREE quote now 👇",
            "cta": "GET_QUOTE",
        },
    ],
    "Christmas Lighting": [
        {
            "headline": "Make Your Home The Best On The Block This Christmas",
            "body": "Skip the ladder. Skip the tangled lights. Skip the frustration.\n\nClean Stream Pro Wash handles everything — custom design, professional installation, and removal after the holidays.\n\n🎄 Commercial-grade LED lights\n🎄 Custom designs for YOUR home\n🎄 Installation AND removal included\n🎄 Free design consultation\n\nSpots fill up fast! Get your free consultation now 👇",
            "cta": "SIGN_UP",
        },
        {
            "headline": "Professional Christmas Lighting - Book Before We're Full!",
            "body": "Every year we book up by mid-October. Don't miss out on making your home the neighborhood showpiece.\n\nClean Stream Pro Wash Christmas Lighting:\n→ Custom design tailored to your home\n→ Professional, insured installation\n→ Takedown & storage after the season\n→ Commercial-grade LED lights included\n\nLimited spots available — claim yours now! 👇",
            "cta": "SIGN_UP",
        },
    ],
}


def list_services():
    print("Available services and ad templates:")
    print()
    for service in BUSINESS_SERVICES:
        has_form = "✅" if service in LEAD_FORM_TEMPLATES else "❌"
        has_copy = "✅" if service in AD_COPY else "❌"
        copy_count = len(AD_COPY.get(service, []))
        print(f"  {service}")
        print(f"    Lead Form: {has_form} | Ad Copy Variants: {copy_count}")


def create_full_ad(service, image_path, daily_budget=15.0, dry_run=False):
    """Create a complete ad: campaign → ad set → lead form → creative → ad."""
    client = MetaAdsClient()

    if service not in LEAD_FORM_TEMPLATES:
        print(f"ERROR: No lead form template for '{service}'")
        print(f"Available: {list(LEAD_FORM_TEMPLATES.keys())}")
        return

    if service not in AD_COPY:
        print(f"ERROR: No ad copy for '{service}'")
        return

    print(f"{'=' * 60}")
    print(f"  CREATING AD: {service}")
    print(f"  Image: {image_path}")
    print(f"  Daily Budget: ${daily_budget:.2f}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'=' * 60}")

    if dry_run:
        template = LEAD_FORM_TEMPLATES[service]
        copies = AD_COPY[service]
        print(f"\n  Would create:")
        print(f"    Campaign: 'CSPW - {service}'")
        print(f"    Ad Set: '{service} - Lead Gen - 25mi Caledonia'")
        print(f"    Lead Form: '{template['name']}'")
        for i, copy in enumerate(copies):
            print(f"    Ad {i+1}: '{copy['headline']}'")
        return

    account_id = client.get_account_id()
    pages = client.get_pages()
    page_id = pages["data"][0]["id"]
    page_access_token = pages["data"][0].get("access_token")

    print(f"  Account: {account_id}")
    print(f"  Page: {pages['data'][0]['name']} ({page_id})")

    # 1. Create campaign
    campaign = client.create_campaign(
        account_id,
        name=f"CSPW - {service}",
        objective="OUTCOME_LEADS",
        status="PAUSED",
    )
    campaign_id = campaign["id"]
    print(f"  ✓ Campaign: {campaign_id}")

    # 2. Create ad set
    adset = client.create_ad_set(
        account_id,
        campaign_id=campaign_id,
        name=f"{service} - Lead Gen - 25mi Caledonia",
        daily_budget=daily_budget,
        targeting=TARGETING,
        optimization_goal="LEAD_GENERATION",
        status="PAUSED",
    )
    adset_id = adset["id"]
    print(f"  ✓ Ad Set: {adset_id}")

    # 3. Create lead form (uses page access token)
    template = LEAD_FORM_TEMPLATES[service]
    # Note: Lead form creation requires page access token
    page_client = MetaAdsClient(access_token=page_access_token or client.access_token)
    try:
        form = page_client.create_lead_form(
            page_id,
            name=template["name"],
            questions=template["questions"],
            privacy_policy_url="https://www.facebook.com/privacy/explanation",  # Update with your privacy policy
            thank_you_message=template["thank_you"],
            context_card=template.get("context_card"),
        )
        form_id = form["id"]
        print(f"  ✓ Lead Form: {form_id}")
    except Exception as e:
        print(f"  ⚠ Lead form creation failed: {e}")
        print(f"    You may need to create it manually or use your existing form.")
        form_id = None

    # 4. Upload image
    try:
        image_hash = client.upload_image(account_id, image_path)
        print(f"  ✓ Image uploaded: {image_hash}")
    except Exception as e:
        print(f"  ✗ Image upload failed: {e}")
        return

    # 5. Create ads for each copy variant
    copies = AD_COPY[service]
    for i, copy in enumerate(copies):
        try:
            creative = client.create_ad_creative(
                account_id,
                name=f"CSPW - {service} - Variant {i+1}",
                page_id=page_id,
                message=copy["body"],
                image_hash=image_hash,
                call_to_action=copy["cta"],
                lead_gen_form_id=form_id,
            )
            creative_id = creative["id"]

            ad = client.create_ad(
                account_id,
                name=f"CSPW - {service} - {copy['headline'][:40]}",
                adset_id=adset_id,
                creative_id=creative_id,
                status="PAUSED",
            )
            print(f"  ✓ Ad {i+1}: {ad['id']} - '{copy['headline']}'")
        except Exception as e:
            print(f"  ✗ Ad {i+1} failed: {e}")

    print(f"\n  Done! All ads created as PAUSED.")
    print(f"  Review in Ads Manager, then activate when ready.")
    print(f"  Campaign ID: {campaign_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Meta lead form ads for Clean Stream Pro Wash")
    parser.add_argument("--service", help="Service to create ads for")
    parser.add_argument("--image", help="Path to ad image")
    parser.add_argument("--budget", type=float, default=15.0, help="Daily budget in dollars (default: $15)")
    parser.add_argument("--list-services", action="store_true", help="List available services")
    parser.add_argument("--create-lead-form", help="Create a lead form for a service")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")

    args = parser.parse_args()

    if args.list_services:
        list_services()
    elif args.service and args.image:
        create_full_ad(args.service, args.image, args.budget, args.dry_run)
    elif args.service and not args.image:
        print("ERROR: --image is required when creating ads")
        print("Usage: python3 create_ads.py --service 'House Washing' --image path/to/image.jpg")
    else:
        parser.print_help()
