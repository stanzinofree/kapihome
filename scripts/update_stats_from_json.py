#!/usr/bin/env python3
"""
Import LinkedIn stats from Tampermonkey-extracted JSON file
Usage: python3 scripts/update_stats_from_json.py <json_file>
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_json_file(file_path: str) -> dict:
    """Load and validate the extracted JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'stats' not in data:
            raise ValueError("Invalid JSON format: missing 'stats' key")
        
        return data
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

def load_linkedin_data() -> tuple[dict, Path]:
    """Load current linkedin.json"""
    json_path = Path(__file__).parent.parent / "data" / "linkedin.json"
    
    if not json_path.exists():
        print(f"❌ Error: linkedin.json not found at {json_path}")
        sys.exit(1)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data, json_path

def save_linkedin_data(data: dict, json_path: Path):
    """Save updated linkedin.json"""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to: {json_path}")

def show_diff(old_stats: dict, new_stats: dict):
    """Show changes between old and new stats"""
    print("\n📊 Changes:")
    print("-" * 60)
    
    changed = False
    for key in new_stats:
        old_val = old_stats.get(key, 0)
        new_val = new_stats[key]
        
        if old_val != new_val:
            changed = True
            diff = new_val - old_val
            symbol = "📈" if diff > 0 else "📉"
            print(f"{symbol} {key}: {old_val} → {new_val} ({diff:+.2f})")
    
    if not changed:
        print("ℹ️  No changes detected")
    
    print("-" * 60)

def find_latest_stats_file() -> str:
    """Find the latest linkedin-stats-*.json in data_tmp/"""
    data_tmp = Path(__file__).parent.parent / "data_tmp"
    if not data_tmp.exists():
        return None
    
    stats_files = list(data_tmp.glob("linkedin-stats-*.json"))
    if not stats_files:
        return None
    
    # Sort by modification time, most recent first
    stats_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(stats_files[0])

def main():
    if len(sys.argv) == 1:
        # No argument: try to find latest file in data_tmp/
        input_file = find_latest_stats_file()
        if not input_file:
            print("❌ No linkedin-stats-*.json file found in data_tmp/")
            print("\nUsage: python3 scripts/update_stats_from_json.py [<stats_json_file>]")
            print("\nOptions:")
            print("  1. Place JSON file in data_tmp/ and run without arguments")
            print("  2. Provide explicit path:")
            print("     python3 scripts/update_stats_from_json.py ~/Downloads/linkedin-stats-2026-01-02.json")
            sys.exit(1)
        print(f"🔍 Auto-detected: {Path(input_file).name}")
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
    else:
        print("Usage: python3 scripts/update_stats_from_json.py [<stats_json_file>]")
        print("\nExample:")
        print("  python3 scripts/update_stats_from_json.py ~/Downloads/linkedin-stats-2026-01-02.json")
        print("  python3 scripts/update_stats_from_json.py  # Auto-finds latest in data_tmp/")
        sys.exit(1)
    
    print("🔄 LinkedIn Stats Importer")
    print("=" * 60)
    
    # Load extracted stats
    print(f"📂 Reading: {input_file}")
    extracted = load_json_file(input_file)
    new_stats = extracted['stats']
    extracted_at = extracted.get('extracted_at', datetime.now().isoformat())
    
    print(f"📅 Extracted at: {extracted_at}")
    
    # Load current linkedin.json
    print("📂 Reading: data/linkedin.json")
    data, json_path = load_linkedin_data()
    old_stats = data.get('stats', {})
    
    # Show diff
    show_diff(old_stats, new_stats)
    
    # Confirm update
    print("\n⚠️  Update linkedin.json with these stats?")
    response = input("Type 'yes' to confirm: ").strip().lower()
    
    if response != 'yes':
        print("❌ Update cancelled")
        sys.exit(0)
    
    # Update stats
    data['stats'] = new_stats
    data['last_updated'] = extracted_at
    
    # Save
    save_linkedin_data(data, json_path)
    
    print("\n✅ Stats updated successfully!")
    print("\n💡 Next steps:")
    print("   1. Restart the Docker services: task restart")
    print("   2. View the updated homepage: http://localhost:3000")

if __name__ == "__main__":
    main()
