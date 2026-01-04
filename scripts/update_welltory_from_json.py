#!/usr/bin/env python3
"""
Welltory Health Stats Import Script

Imports Welltory health metrics from JSON file into KapiHome data storage.
Supports auto-detection of latest file in data_tmp/ directory.

Usage:
    python3 update_welltory_from_json.py                    # Auto-detect latest file
    python3 update_welltory_from_json.py path/to/file.json  # Specific file
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


def find_latest_welltory_file() -> Path:
    """Find the most recent welltory-stats*.json file in data_tmp/"""
    data_tmp = Path(__file__).parent.parent / "data_tmp"
    
    if not data_tmp.exists():
        raise FileNotFoundError(
            f"data_tmp/ directory not found at {data_tmp}\n"
            "Create it with: mkdir data_tmp"
        )
    
    # Find all welltory stats files
    welltory_files = list(data_tmp.glob("welltory-stats*.json"))
    
    if not welltory_files:
        raise FileNotFoundError(
            "No welltory-stats*.json files found in data_tmp/\n\n"
            "Run the Tampermonkey script on https://app.welltory.com/\n"
            "Move the downloaded file to data_tmp/"
        )
    
    # Sort by modification time (most recent first)
    welltory_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest_file = welltory_files[0]
    
    print(f"📊 Found: {latest_file.name}")
    print(f"📅 Modified: {datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    return latest_file


def load_welltory_data(file_path: Path) -> dict:
    """Load and validate Welltory JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate structure
    if 'stats' not in data:
        raise ValueError("Invalid Welltory JSON: missing 'stats' field")
    
    return data


def calculate_trends(new_data: dict, old_data: dict | None) -> dict:
    """Calculate trends compared to previous data"""
    trends = {}
    
    if not old_data or 'stats' not in old_data:
        return trends
    
    new_stats = new_data.get('stats', {})
    old_stats = old_data.get('stats', {})
    
    for key in ['stress', 'energy', 'productivity', 'hrv', 'resting_heart_rate', 'sleep_quality', 'mood']:
        new_val = new_stats.get(key)
        old_val = old_stats.get(key)
        
        if new_val is not None and old_val is not None:
            diff = new_val - old_val
            trends[key] = {
                'value': new_val,
                'previous': old_val,
                'change': diff,
                'direction': '↑' if diff > 0 else '↓' if diff < 0 else '→'
            }
    
    return trends


def show_preview(data: dict, trends: dict):
    """Show preview of Welltory data"""
    print("\n" + "="*70)
    print("🏥 WELLTORY HEALTH DATA PREVIEW")
    print("="*70)
    
    stats = data.get('stats', {})
    date = data.get('date', 'Unknown')
    extracted_at = data.get('extracted_at', '')
    
    print(f"\n📅 Date: {date}")
    if extracted_at:
        try:
            dt = datetime.fromisoformat(extracted_at.replace('Z', '+00:00'))
            print(f"🕐 Extracted: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            pass
    
    print(f"\n📊 Current Metrics:")
    
    metrics = [
        ('stress', 'Stress Level', '😰'),
        ('energy', 'Energy Level', '⚡'),
        ('productivity', 'Productivity', '🎯'),
        ('hrv', 'Heart Rate Variability', '❤️'),
        ('resting_heart_rate', 'Resting HR', '💓'),
        ('sleep_quality', 'Sleep Quality', '😴'),
        ('mood', 'Mood', '😊')
    ]
    
    for key, label, icon in metrics:
        value = stats.get(key)
        if value is not None:
            trend_info = trends.get(key, {})
            if trend_info:
                change = trend_info.get('change', 0)
                direction = trend_info.get('direction', '')
                change_str = f" {direction} {abs(change):.1f}"
            else:
                change_str = ""
            
            print(f"   {icon} {label}: {value}{change_str}")
        else:
            print(f"   {icon} {label}: Not available")
    
    # Health insights
    print(f"\n💡 Quick Insights:")
    
    stress = stats.get('stress')
    energy = stats.get('energy')
    hrv = stats.get('hrv')
    
    if stress is not None:
        if stress < 30:
            print(f"   ✅ Low stress level ({stress}) - Great!")
        elif stress < 60:
            print(f"   ⚠️  Moderate stress level ({stress})")
        else:
            print(f"   🚨 High stress level ({stress}) - Consider relaxation")
    
    if energy is not None:
        if energy > 70:
            print(f"   ⚡ High energy level ({energy}) - Excellent!")
        elif energy > 40:
            print(f"   😌 Moderate energy level ({energy})")
        else:
            print(f"   😴 Low energy level ({energy}) - Rest needed")
    
    if hrv is not None:
        if hrv > 60:
            print(f"   ❤️  Excellent HRV ({hrv}) - Great recovery!")
        elif hrv > 40:
            print(f"   👍 Good HRV ({hrv})")
        else:
            print(f"   ⚠️  Low HRV ({hrv}) - Recovery needed")
    
    print("\n" + "="*70)


def save_data(data: dict, dest_path: Path):
    """Save data to destination file"""
    # Ensure data directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure we have historical_data array
    if 'historical_data' not in data:
        data['historical_data'] = []
    
    # Write data
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Data saved to: {dest_path}")


def merge_with_existing(new_data: dict, old_data: dict | None) -> dict:
    """Merge new data with existing historical data"""
    if not old_data:
        # First import - create structure
        merged = {
            'current': new_data.get('stats', {}),
            'date': new_data.get('date'),
            'last_updated': new_data.get('extracted_at'),
            'historical_data': [
                {
                    'date': new_data.get('date'),
                    'stats': new_data.get('stats', {}),
                    'extracted_at': new_data.get('extracted_at')
                }
            ]
        }
        return merged
    
    # Update current stats
    merged = old_data.copy()
    merged['current'] = new_data.get('stats', {})
    merged['date'] = new_data.get('date')
    merged['last_updated'] = new_data.get('extracted_at')
    
    # Add to historical data
    if 'historical_data' not in merged:
        merged['historical_data'] = []
    
    # Add new entry
    merged['historical_data'].append({
        'date': new_data.get('date'),
        'stats': new_data.get('stats', {}),
        'extracted_at': new_data.get('extracted_at')
    })
    
    # Keep only last 90 days of history
    merged['historical_data'] = sorted(
        merged['historical_data'],
        key=lambda x: x.get('date', ''),
        reverse=True
    )[:90]
    
    return merged


def main():
    """Main execution"""
    try:
        # Determine source file
        if len(sys.argv) > 1:
            source_file = Path(sys.argv[1])
            if not source_file.exists():
                print(f"❌ File not found: {source_file}", file=sys.stderr)
                return 1
            print(f"📄 Using specified file: {source_file.name}")
        else:
            print("🔍 Searching for latest Welltory file in data_tmp/...\n")
            source_file = find_latest_welltory_file()
        
        # Load new data
        print(f"\n📖 Loading data from {source_file.name}...")
        new_data = load_welltory_data(source_file)
        
        # Load existing data if available
        dest_path = Path(__file__).parent.parent / "data" / "welltory.json"
        old_data = None
        
        if dest_path.exists():
            with open(dest_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        
        # Calculate trends
        trends = calculate_trends(new_data, old_data)
        
        # Show preview
        show_preview(new_data, trends)
        
        # Confirm import
        response = input("\n❓ Import this data? [y/N]: ").strip().lower()
        
        if response != 'y':
            print("\n❌ Import cancelled")
            return 1
        
        # Merge with existing data
        merged_data = merge_with_existing(new_data, old_data)
        
        # Save
        save_data(merged_data, dest_path)
        
        print("\n🎉 Welltory data imported successfully!")
        print("\n📍 Next steps:")
        print("   1. Data is ready for use")
        print("   2. Restart backend if needed: docker restart kapihome-backend")
        print("   3. Visit: http://localhost:3000")
        
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
