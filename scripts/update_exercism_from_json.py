#!/usr/bin/env python3
"""
Import Exercism data from Tampermonkey-extracted JSON file
Usage: python3 scripts/update_exercism_from_json.py <exercism_json_file>
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_exercism_json(file_path: str) -> dict:
    """Load the extracted Exercism JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate structure
        required_keys = ['profile', 'stats', 'badges']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Invalid JSON format: missing '{key}' key")
        
        return data
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file: {e}")
        sys.exit(1)

def get_exercism_json_path() -> Path:
    """Get the path to exercism.json"""
    json_path = Path(__file__).parent.parent / "data" / "exercism.json"
    return json_path

def save_exercism_data(data: dict, json_path: Path):
    """Save Exercism data to JSON file"""
    # Ensure data directory exists
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to: {json_path}")

def find_latest_exercism_file() -> str:
    """Find the latest exercism-data-*.json in data_tmp/"""
    data_tmp = Path(__file__).parent.parent / "data_tmp"
    if not data_tmp.exists():
        return None
    
    exercism_files = list(data_tmp.glob("exercism-data-*.json"))
    if not exercism_files:
        return None
    
    # Sort by modification time, most recent first
    exercism_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(exercism_files[0])

def main():
    if len(sys.argv) == 1:
        # No argument: try to find latest file in data_tmp/
        input_file = find_latest_exercism_file()
        if not input_file:
            print("❌ No exercism-data-*.json file found in data_tmp/")
            print("\nUsage: python3 scripts/update_exercism_from_json.py [<exercism_json_file>]")
            print("\nOptions:")
            print("  1. Place JSON file in data_tmp/ and run without arguments")
            print("  2. Provide explicit path:")
            print("     python3 scripts/update_exercism_from_json.py ~/Downloads/exercism-data-2026-01-02.json")
            sys.exit(1)
        print(f"🔍 Auto-detected: {Path(input_file).name}")
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
    else:
        print("Usage: python3 scripts/update_exercism_from_json.py [<exercism_json_file>]")
        print("\nExample:")
        print("  python3 scripts/update_exercism_from_json.py ~/Downloads/exercism-data-2026-01-02.json")
        print("  python3 scripts/update_exercism_from_json.py  # Auto-finds latest in data_tmp/")
        sys.exit(1)
    
    print("🎯 Exercism Data Importer")
    print("=" * 60)
    
    # Load extracted data
    print(f"📂 Reading: {input_file}")
    data = load_exercism_json(input_file)
    
    extracted_at = data.get('extracted_at', datetime.now().isoformat())
    profile = data.get('profile', {})
    stats = data.get('stats', {})
    badges = data.get('badges', [])
    tracks = data.get('tracks', [])
    solutions = data.get('recent_solutions', [])
    
    # Display preview
    print(f"📅 Extracted at: {extracted_at}")
    print("\n👤 Profile:")
    print(f"   Username: {profile.get('username', 'N/A')}")
    print(f"   Location: {profile.get('location', 'N/A')}")
    
    print("\n📊 Stats:")
    print(f"   Reputation: {stats.get('reputation', 0)}")
    print(f"   Total Badges: {stats.get('total_badges', len(badges))}")
    print(f"   Total Solutions: {stats.get('total_solutions', 0)}")
    print(f"   Total Tracks: {stats.get('total_tracks', len(tracks))}")
    
    if badges:
        print(f"\n🏆 Badges ({len(badges)}):")
        badge_by_rarity = stats.get('badges_by_rarity', {})
        if badge_by_rarity:
            print(f"   Common: {badge_by_rarity.get('common', 0)}")
            print(f"   Rare: {badge_by_rarity.get('rare', 0)}")
            print(f"   Ultimate: {badge_by_rarity.get('ultimate', 0)}")
            print(f"   Legendary: {badge_by_rarity.get('legendary', 0)}")
        
        print("\n   Badge list:")
        for badge in badges[:5]:  # Show max 5
            print(f"   - {badge.get('name', 'Unknown')} ({badge.get('rarity', 'unknown')})")
        if len(badges) > 5:
            print(f"   ... and {len(badges) - 5} more")
    
    if tracks:
        print(f"\n💻 Tracks ({len(tracks)}):")
        for track in tracks[:5]:  # Show max 5
            print(f"   - {track.get('name', 'Unknown')}: {track.get('exercises_completed', 0)} exercises")
        if len(tracks) > 5:
            print(f"   ... and {len(tracks) - 5} more")
    
    if solutions:
        print(f"\n📝 Recent Solutions ({len(solutions)}):")
        for sol in solutions[:3]:  # Show max 3
            print(f"   - {sol.get('exercise', 'Unknown')} ({sol.get('track', 'Unknown')})")
            print(f"     Published: {sol.get('published_at', 'Unknown')}")
    
    print("\n" + "=" * 60)
    
    # Confirm update
    json_path = get_exercism_json_path()
    
    if json_path.exists():
        print(f"⚠️  File {json_path} already exists and will be OVERWRITTEN")
    else:
        print(f"📝 Will create new file: {json_path}")
    
    print("\n⚠️  Proceed with import?")
    response = input("Type 'yes' to confirm: ").strip().lower()
    
    if response != 'yes':
        print("❌ Import cancelled")
        sys.exit(0)
    
    # Save data
    save_exercism_data(data, json_path)
    
    print("\n✅ Exercism data imported successfully!")
    print("\n💡 Next steps:")
    print("   1. Restart the Docker services: task restart")
    print("   2. View the updated homepage: http://localhost:3000")

if __name__ == "__main__":
    main()
