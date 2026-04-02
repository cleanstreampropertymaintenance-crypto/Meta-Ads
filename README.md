# Clean Stream Pro Wash - Meta Ads Management System

## Quick Start

```bash
# Install dependency
pip install requests

# 1. Audit all current ads (read-only, no changes)
python3 audit.py

# 2. Optimize: pause losers, identify winners (dry run first!)
python3 optimize.py --dry-run    # Preview changes
python3 optimize.py              # Make changes

# 3. Consolidate winners into dedicated campaigns
python3 consolidate_winners.py --dry-run
python3 consolidate_winners.py

# 4. Create new ads
python3 create_ads.py --list-services
python3 create_ads.py --service "House Washing" --image ~/photos/house-wash.jpg
python3 create_ads.py --service "Christmas Lighting" --image ~/photos/xmas.jpg --budget 20

# Or run the full pipeline
python3 run_all.py --dry-run     # Preview everything
python3 run_all.py               # Run everything
```

## How It Works

### Grading System
- **A (Winner)**: CPL under $15 — push budget here
- **B (Decent)**: CPL $15-$25 — keep running, monitor
- **C (Underperformer)**: CPL above $25 or low CTR — consider pausing
- **F (Turn Off)**: High spend + zero/terrible results — auto-paused
- **NEW**: Not enough spend data yet — let it run

### Targeting (Pre-configured)
- 25-mile radius of 6634 Avalon Dr SE, Caledonia, MI
- Exclusions: Big Rapids, Detroit, Kalamazoo, Lansing, Mount Pleasant, Muskegon County
- Ages 25-65
- All ads are Lead Form ads optimized for lead generation

### Configuration
Edit `config.py` to adjust:
- Performance thresholds (CPL targets, min spend before evaluation)
- Targeting parameters
- API token (when it expires, update here)

## Creating New Ads

```bash
# See all available services and templates
python3 create_ads.py --list-services

# Create ads with an image you shot
python3 create_ads.py --service "House Washing" --image before-after.jpg --budget 15

# All ads are created PAUSED — review in Ads Manager before activating
```

## Files
- `config.py` — All configuration (token, targeting, thresholds)
- `meta_client.py` — Meta Graph API client library
- `audit.py` — Pulls and grades all current ads
- `optimize.py` — Pauses losers, identifies winners
- `consolidate_winners.py` — Creates "Winners" campaigns
- `create_ads.py` — Creates new lead form ads with image creatives
- `run_all.py` — Runs the full audit → optimize → consolidate pipeline

## Token Management
Your Meta access token expires periodically. When it does:
1. Go to [Meta Business Suite](https://business.facebook.com/settings/system-users)
2. Generate a new token with `ads_management`, `ads_read`, `pages_manage_ads`, `leads_retrieval` permissions
3. Update the token in `config.py`
