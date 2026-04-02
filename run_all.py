#!/usr/bin/env python3
"""
MASTER SCRIPT: Run the full Meta Ads optimization pipeline
1. Audit all ads
2. Optimize (pause losers)
3. Consolidate winners
4. Show creative recommendations

Usage:
  python3 run_all.py              # Full pipeline (makes changes!)
  python3 run_all.py --dry-run    # Preview only, no changes
  python3 run_all.py --audit-only # Just run the audit
"""

import sys
import subprocess

def run_script(name, args=None):
    cmd = [sys.executable, name] + (args or [])
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0

def main():
    dry_run = "--dry-run" in sys.argv
    audit_only = "--audit-only" in sys.argv
    extra_args = ["--dry-run"] if dry_run else []

    print("\n" + "=" * 70)
    print("  CLEAN STREAM PRO WASH - META ADS MANAGEMENT PIPELINE")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 70)

    # Step 1: Audit
    print("\n\n>>> STEP 1: AUDITING ALL ADS <<<\n")
    if not run_script("audit.py"):
        print("Audit failed. Fix errors and retry.")
        sys.exit(1)

    if audit_only:
        print("\nAudit complete. Use --dry-run or run without flags for full pipeline.")
        return

    # Step 2: Optimize
    print("\n\n>>> STEP 2: OPTIMIZING ADS <<<\n")
    run_script("optimize.py", extra_args)

    # Step 3: Consolidate winners
    print("\n\n>>> STEP 3: CONSOLIDATING WINNERS <<<\n")
    run_script("consolidate_winners.py", extra_args)

    # Done
    print("\n\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    print("  Next steps:")
    print("  1. Review paused/optimized ads in Meta Ads Manager")
    print("  2. Activate winning campaigns when ready")
    print("  3. Create new ads: python3 create_ads.py --list-services")
    print("  4. Upload new creatives and run create_ads.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
