#!/usr/bin/env python3
"""
Import LinkedIn posts from Tampermonkey-extracted JSON file
Usage: python3 scripts/update_posts_from_json.py <posts_json_file>
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_posts_json(file_path: str) -> dict:
    """Load the extracted posts JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'recent_posts' not in data:
            raise ValueError("Invalid JSON format: missing 'recent_posts' key")
        
        return data
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file: {e}")
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

def find_latest_posts_file() -> str:
    """Find the latest linkedin-posts-*.json in data_tmp/"""
    data_tmp = Path(__file__).parent.parent / "data_tmp"
    if not data_tmp.exists():
        return None
    
    posts_files = list(data_tmp.glob("linkedin-posts-*.json"))
    if not posts_files:
        return None
    
    # Sort by modification time, most recent first
    posts_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(posts_files[0])

def main():
    if len(sys.argv) == 1:
        # No argument: try to find latest file in data_tmp/
        input_file = find_latest_posts_file()
        if not input_file:
            print("❌ No linkedin-posts-*.json file found in data_tmp/")
            print("\nUsage: python3 scripts/update_posts_from_json.py [<posts_json_file>]")
            print("\nOptions:")
            print("  1. Place JSON file in data_tmp/ and run without arguments")
            print("  2. Provide explicit path:")
            print("     python3 scripts/update_posts_from_json.py ~/Downloads/linkedin-posts-2026-01-02.json")
            sys.exit(1)
        print(f"🔍 Auto-detected: {Path(input_file).name}")
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
    else:
        print("Usage: python3 scripts/update_posts_from_json.py [<posts_json_file>]")
        print("\nExample:")
        print("  python3 scripts/update_posts_from_json.py ~/Downloads/linkedin-posts-2026-01-02.json")
        print("  python3 scripts/update_posts_from_json.py  # Auto-finds latest in data_tmp/")
        sys.exit(1)
    
    print("📝 LinkedIn Posts Importer")
    print("=" * 60)
    
    # Load extracted posts
    print(f"📂 Reading: {input_file}")
    extracted = load_posts_json(input_file)
    new_posts = extracted['recent_posts']
    extracted_at = extracted.get('extracted_at', datetime.now().isoformat())
    
    print(f"📅 Extracted at: {extracted_at}")
    print(f"📊 Found {len(new_posts)} posts")
    
    # Load current linkedin.json
    print("📂 Reading: data/linkedin.json")
    data, json_path = load_linkedin_data()
    
    # Show posts
    print("\n📝 Posts to import:")
    print("-" * 60)
    for i, post in enumerate(new_posts, 1):
        print(f"{i}. {post.get('title', 'No title')[:60]}...")
        print(f"   Date: {post.get('date', 'Unknown')}")
    print("-" * 60)
    
    # Confirm update
    print("\n⚠️  Replace posts in linkedin.json?")
    response = input("Type 'yes' to confirm: ").strip().lower()
    
    if response != 'yes':
        print("❌ Update cancelled")
        sys.exit(0)
    
    # Update posts
    data['recent_posts'] = new_posts
    data['last_updated'] = extracted_at
    
    # Save
    save_linkedin_data(data, json_path)
    
    print("\n✅ Posts updated successfully!")
    print("\n💡 Next steps:")
    print("   1. Restart the Docker services: task restart")
    print("   2. View the updated homepage: http://localhost:3000")

if __name__ == "__main__":
    main()
