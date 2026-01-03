#!/usr/bin/env python3
"""
GitHub Stats Import Script

Imports GitHub profile data from JSON file into KapiHome data storage.
Supports auto-detection of latest file in data_tmp/ directory.

Usage:
    python3 update_github_from_json.py                    # Auto-detect latest file
    python3 update_github_from_json.py path/to/file.json  # Specific file
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def find_latest_github_file() -> str:
    """Find the latest github-data-*.json in data_tmp/"""
    data_tmp = Path(__file__).parent.parent / "data_tmp"
    
    if not data_tmp.exists():
        raise FileNotFoundError(
            f"data_tmp/ directory not found at {data_tmp}\n"
            "Create it with: mkdir data_tmp"
        )
    
    github_files = list(data_tmp.glob("github-data-*.json"))
    
    if not github_files:
        raise FileNotFoundError(
            "No github-data-*.json files found in data_tmp/\n"
            "Run the Tampermonkey script first and move the downloaded file to data_tmp/"
        )
    
    # Sort by modification time, most recent first
    github_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest = github_files[0]
    
    print(f"📁 Auto-detected file: {latest.name}")
    print(f"   Modified: {datetime.fromtimestamp(latest.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    return str(latest)


def load_json(file_path: str) -> dict:
    """Load and validate JSON file"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate structure
    required_keys = ['profile', 'stats', 'top_languages', 'top_repos']
    missing_keys = [k for k in required_keys if k not in data]
    
    if missing_keys:
        raise ValueError(f"Invalid data structure. Missing keys: {missing_keys}")
    
    return data


def show_diff(new_data: dict, old_data: dict | None):
    """Show differences between new and old data"""
    print("\n" + "="*70)
    print("📊 GITHUB DATA PREVIEW")
    print("="*70)
    
    profile = new_data.get('profile', {})
    stats = new_data.get('stats', {})
    langs = new_data.get('top_languages', [])
    repos = new_data.get('top_repos', [])
    
    print(f"\n👤 Profile: {profile.get('name', 'N/A')} (@{profile.get('username', 'N/A')})")
    print(f"   Bio: {profile.get('bio', 'N/A')[:60]}...")
    print(f"   Location: {profile.get('location', 'N/A')}")
    
    print(f"\n📈 Stats:")
    print(f"   Public Repos: {stats.get('public_repos', 0)}")
    print(f"   Total Stars: {stats.get('total_stars', 0)}")
    print(f"   Followers: {stats.get('followers', 0)}")
    print(f"   Contributions (year): {stats.get('contributions_last_year', 0)}")
    print(f"   Current Streak: {stats.get('current_streak', 0)} days")
    
    if old_data:
        old_stats = old_data.get('stats', {})
        print(f"\n🔄 Changes:")
        
        for key in ['public_repos', 'total_stars', 'followers', 'contributions_last_year']:
            old_val = old_stats.get(key, 0)
            new_val = stats.get(key, 0)
            diff = new_val - old_val
            
            if diff != 0:
                sign = '+' if diff > 0 else ''
                print(f"   {key}: {old_val} → {new_val} ({sign}{diff})")
    
    print(f"\n💻 Top {len(langs)} Languages:")
    for lang in langs[:3]:
        print(f"   - {lang['name']}: {lang['count']} repos ({lang['percentage']}%)")
    
    print(f"\n⭐ Top {len(repos)} Repositories:")
    for repo in repos[:3]:
        print(f"   - {repo['name']}: {repo['stars']} ⭐")
    
    print("\n" + "="*70)


def save_data(data: dict, dest_path: Path):
    """Save data to destination file"""
    # Ensure data directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write data
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Data saved to: {dest_path}")


def main():
    """Main execution"""
    try:
        # Determine source file
        if len(sys.argv) > 1:
            source_file = sys.argv[1]
            print(f"📁 Using specified file: {source_file}")
        else:
            source_file = find_latest_github_file()
        
        # Load new data
        print(f"\n📖 Loading data from: {source_file}")
        new_data = load_json(source_file)
        
        # Load existing data if available
        dest_path = Path(__file__).parent.parent / "data" / "github.json"
        old_data = None
        
        if dest_path.exists():
            with open(dest_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        
        # Show preview
        show_diff(new_data, old_data)
        
        # Confirm
        response = input("\n❓ Import this data? [y/N]: ").strip().lower()
        
        if response != 'y':
            print("\n❌ Import cancelled")
            return 1
        
        # Save
        save_data(new_data, dest_path)
        
        print("\n🎉 GitHub data imported successfully!")
        print("\n📍 Next steps:")
        print("   1. Restart the frontend: docker restart kapihome-frontend")
        print("   2. Visit: http://localhost:3000/github")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
