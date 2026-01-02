#!/usr/bin/env python3
"""
LinkedIn Stats Updater - Manual Input Helper
Helps you update LinkedIn statistics by copying numbers from the dashboard.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_current_data():
    """Load current linkedin.json data"""
    json_path = Path(__file__).parent.parent / "data" / "linkedin.json"
    
    if not json_path.exists():
        print(f"❌ Error: {json_path} not found!")
        sys.exit(1)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f), json_path

def save_data(data, json_path):
    """Save updated data to linkedin.json"""
    data["last_updated"] = datetime.now().isoformat()
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Stats updated successfully!")
    print(f"📁 File: {json_path}")
    print(f"🕒 Last updated: {data['last_updated']}")

def get_int_input(prompt, current_value=None):
    """Get integer input with optional current value"""
    if current_value is not None:
        full_prompt = f"{prompt} [current: {current_value}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        try:
            value = input(full_prompt).strip()
            if not value and current_value is not None:
                return current_value
            return int(value)
        except ValueError:
            print("❌ Invalid number, try again")

def get_float_input(prompt, current_value=None):
    """Get float input with optional current value"""
    if current_value is not None:
        full_prompt = f"{prompt} [current: {current_value}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        try:
            value = input(full_prompt).strip()
            if not value and current_value is not None:
                return current_value
            return float(value)
        except ValueError:
            print("❌ Invalid number, try again")

def update_stats_interactive():
    """Interactive stats update"""
    print("=" * 60)
    print("🔄 LinkedIn Stats Updater")
    print("=" * 60)
    print("\n📊 Open: https://www.linkedin.com/dashboard/")
    print("💡 Tip: Press ENTER to keep current value\n")
    
    data, json_path = load_current_data()
    current_stats = data.get("stats", {})
    
    print("--- Profile Views ---")
    stats = {
        "profile_views_7d": get_int_input(
            "Profile views (7 days)", 
            current_stats.get("profile_views_7d")
        ),
        "profile_views_30d": get_int_input(
            "Profile views (30 days)", 
            current_stats.get("profile_views_30d")
        ),
        "profile_views_90d": get_int_input(
            "Profile views (90 days)", 
            current_stats.get("profile_views_90d")
        ),
    }
    
    print("\n--- Post Performance ---")
    stats.update({
        "post_impressions_7d": get_int_input(
            "Post impressions (7 days)", 
            current_stats.get("post_impressions_7d")
        ),
        "post_impressions_30d": get_int_input(
            "Post impressions (30 days)", 
            current_stats.get("post_impressions_30d")
        ),
    })
    
    print("\n--- Search & Discovery ---")
    stats.update({
        "search_appearances_7d": get_int_input(
            "Search appearances (7 days)", 
            current_stats.get("search_appearances_7d")
        ),
        "search_appearances_30d": get_int_input(
            "Search appearances (30 days)", 
            current_stats.get("search_appearances_30d")
        ),
    })
    
    print("\n--- Network Growth ---")
    stats.update({
        "followers": get_int_input(
            "Total followers", 
            current_stats.get("followers")
        ),
        "connection_growth_7d": get_int_input(
            "New connections (7 days)", 
            current_stats.get("connection_growth_7d")
        ),
    })
    
    print("\n--- Engagement ---")
    stats["engagement_rate"] = get_float_input(
        "Engagement rate (%)", 
        current_stats.get("engagement_rate")
    )
    
    # Update data
    data["stats"] = stats
    save_data(data, json_path)
    
    # Show summary
    print("\n" + "=" * 60)
    print("📈 Updated Stats Summary")
    print("=" * 60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        update_stats_interactive()
    except KeyboardInterrupt:
        print("\n\n⚠️  Update cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
