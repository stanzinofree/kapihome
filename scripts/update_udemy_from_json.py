#!/usr/bin/env python3
"""
Udemy Student Stats Import Script

Imports Udemy learning data from JSON file into KapiHome data storage.
Supports auto-detection of latest file in data_tmp/ directory.

Usage:
    python3 update_udemy_from_json.py                    # Auto-detect latest file
    python3 update_udemy_from_json.py path/to/file.json  # Specific file
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def find_udemy_files() -> dict:
    """Find the 3 Udemy JSON files in data_tmp/"""
    data_tmp = Path(__file__).parent.parent / "data_tmp"
    
    if not data_tmp.exists():
        raise FileNotFoundError(
            f"data_tmp/ directory not found at {data_tmp}\n"
            "Create it with: mkdir data_tmp"
        )
    
    # Find each type of file
    stats_files = list(data_tmp.glob("udemy-stats*.json"))
    in_progress_files = list(data_tmp.glob("udemy-in-progress*.json"))
    not_started_files = list(data_tmp.glob("udemy-not-started*.json"))
    
    files = {}
    
    if stats_files:
        stats_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        files['stats'] = stats_files[0]
        print(f"📊 Stats: {files['stats'].name}")
    
    if in_progress_files:
        in_progress_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        files['in_progress'] = in_progress_files[0]
        print(f"📚 In-Progress: {files['in_progress'].name}")
    
    if not_started_files:
        not_started_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        files['not_started'] = not_started_files[0]
        print(f"📝 Not-Started: {files['not_started'].name}")
    
    if not files:
        raise FileNotFoundError(
            "No udemy-*.json files found in data_tmp/\n\n"
            "Run these 3 Tampermonkey scripts:\n"
            "1. udemy-main-stats-extractor.user.js (on /home/my-courses/)\n"
            "2. udemy-in-progress-extractor.user.js (on /learning/?progress_filter=in-progress)\n"
            "3. udemy-not-started-extractor.user.js (on /learning/?progress_filter=not-started)\n\n"
            "Move all downloaded files to data_tmp/"
        )
    
    return files


def load_and_combine_files(files: dict) -> dict:
    """Load and combine the 3 JSON files into final structure"""
    
    # Load stats file
    stats_data = {}
    if 'stats' in files:
        with open(files['stats'], 'r', encoding='utf-8') as f:
            stats_json = json.load(f)
            stats_data = stats_json.get('stats', {})
    
    # Load in-progress courses
    in_progress_courses = []
    if 'in_progress' in files:
        with open(files['in_progress'], 'r', encoding='utf-8') as f:
            in_progress_json = json.load(f)
            in_progress_courses = in_progress_json.get('courses', [])
    
    # Load not-started courses
    not_started_courses = []
    if 'not_started' in files:
        with open(files['not_started'], 'r', encoding='utf-8') as f:
            not_started_json = json.load(f)
            not_started_courses = not_started_json.get('courses', [])
    
    # Separate completed from in-progress
    completed_courses = [c for c in in_progress_courses if c.get('progress', 0) >= 100]
    actual_in_progress = [c for c in in_progress_courses if 0 < c.get('progress', 0) < 100]
    
    # Calculate totals
    total_courses = stats_data.get('total_courses', 0)
    if total_courses == 0:
        total_courses = len(completed_courses) + len(actual_in_progress) + len(not_started_courses)
    
    completion_rate = int((len(completed_courses) / total_courses * 100)) if total_courses > 0 else 0
    
    # Build combined data structure
    combined_data = {
        "student": {
            "total_courses": total_courses,
            "completed_courses": len(completed_courses),
            "in_progress_courses": len(actual_in_progress),
            "weekly_minutes_current": stats_data.get('weekly_minutes_current', 0),
            "weekly_minutes_goal": stats_data.get('weekly_minutes_goal', 30),
            "visits_this_week": stats_data.get('visits_this_week', 0),
            "visits_last_week": stats_data.get('visits_last_week', 0),
            "weekly_streak": stats_data.get('weekly_streak', 0)
        },
        "stats": {
            "total_enrolled": total_courses,
            "completed": len(completed_courses),
            "in_progress": len(actual_in_progress),
            "completion_rate": completion_rate,
            "weekly_minutes": f"{stats_data.get('weekly_minutes_current', 0)}/{stats_data.get('weekly_minutes_goal', 30)}",
            "weekly_visits": f"{stats_data.get('visits_this_week', 0)}/{stats_data.get('visits_last_week', 0)}",
            "streak_weeks": stats_data.get('weekly_streak', 0)
        },
        "completed_courses": completed_courses[:20],
        "in_progress_courses": actual_in_progress[:20],
        "not_started_courses": not_started_courses[:20],
        "last_updated": datetime.now().isoformat()
    }
    
    return combined_data


def show_diff(new_data: dict, old_data: dict | None):
    """Show differences between new and old data"""
    print("\n" + "="*70)
    print("📚 UDEMY STUDENT DATA PREVIEW")
    print("="*70)
    
    student = new_data.get('student', {})
    stats = new_data.get('stats', {})
    completed = new_data.get('completed_courses', [])
    in_progress = new_data.get('in_progress_courses', [])
    
    print(f"\n📊 Learning Stats:")
    print(f"   Total Courses: {student.get('total_courses', 0)}")
    print(f"   Completed: {student.get('completed_courses', 0)}")
    print(f"   In Progress: {student.get('in_progress_courses', 0)}")
    print(f"   Completion Rate: {stats.get('completion_rate', 0)}%")
    
    print(f"\n📅 Weekly Activity:")
    print(f"   Minutes: {student.get('weekly_minutes_current', 0)}/{student.get('weekly_minutes_goal', 30)}")
    print(f"   Visits: {student.get('visits_this_week', 0)}/{student.get('visits_last_week', 0)} (questa/scorsa)")
    print(f"   Streak: {student.get('weekly_streak', 0)} settimane consecutive")
    
    if old_data:
        old_student = old_data.get('student', {})
        print(f"\n🔄 Changes:")
        
        for key, label in [
            ('total_courses', 'Total Courses'),
            ('completed_courses', 'Completed'),
            ('weekly_minutes_current', 'Weekly Minutes'),
            ('visits_this_week', 'Visits This Week'),
            ('weekly_streak', 'Weekly Streak')
        ]:
            old_val = old_student.get(key, 0)
            new_val = student.get(key, 0)
            diff = new_val - old_val
            
            if diff != 0:
                sign = '+' if diff > 0 else ''
                print(f"   {label}: {old_val} → {new_val} ({sign}{diff})")
    
    print(f"\n✅ Recently Completed ({len(completed)} total):")
    for course in completed[:3]:
        print(f"   - {course['title']}")
    
    print(f"\n📖 In Progress ({len(in_progress)} total):")
    for course in in_progress[:3]:
        print(f"   - {course['title']} ({course.get('progress', 0)}%)")
    
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
        print("🔍 Searching for Udemy JSON files in data_tmp/...\n")
        
        # Find the 3 files
        files = find_udemy_files()
        
        if len(files) < 3:
            print("\n⚠️  Warning: Not all files found!")
            print("Missing files will use default values (0)")
            response = input("\nContinue anyway? [y/N]: ").strip().lower()
            if response != 'y':
                print("\n❌ Import cancelled")
                return 1
        
        # Load and combine data
        print(f"\n📖 Combining data from {len(files)} file(s)...")
        new_data = load_and_combine_files(files)
        
        # Load existing data if available
        dest_path = Path(__file__).parent.parent / "data" / "udemy.json"
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
        
        print("\n🎉 Udemy data imported successfully!")
        print("\n📍 Next steps:")
        print("   1. Restart backend: docker restart kapihome-backend")
        print("   2. Visit: http://localhost:3000")
        
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
